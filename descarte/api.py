import os
import uuid
from typing import List, Optional
from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
    WebSocket,
    WebSocketDisconnect,
    BackgroundTasks,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .main import (
    cadastrar_coletor,
    publicar_item,
    criar_item_temporario,
    ativar_item_e_notificar,
    rejeitar_item,
    aceitar_match,
    listar_itens_proximos,
    limpar_itens_expirados,
    store,
)
from .db import listar_coletores
from .models import Item
from .proximity import find_matches
from .notify import gerenciador_notificacoes
from .routing import otimizador_rotas
from .historico import gerenciador_historico, criar_tabela_historico
from .impact import calculadora_impacto


criar_tabela_historico()

app = FastAPI(
    title="Tinder do Descarte",
    description="API para descarte responsável de resíduos volumosos",
    version="0.7.0",
)

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------- Simulação de IA de triagem ----------

def analisar_imagem_com_ia(file_path: str) -> dict:
    nome = file_path.lower()

    if any(palavra in nome for palavra in ["lixo", "organico", "resto", "comida"]):
        return {
            "valido": False,
            "categoria": "Desconhecido",
            "confianca": 0.12,
            "motivo": "Imagem detectada como possível lixo doméstico ou orgânico",
        }

    if any(p in nome for p in ["sofa", "cadeira", "mesa", "madeira", "movel"]):
        categoria = "madeira"
    elif any(p in nome for p in ["tv", "monitor", "notebook", "celular", "eletronico"]):
        categoria = "eletronico"
    elif any(p in nome for p in ["ferro", "metal", "alumínio", "aluminio"]):
        categoria = "metal"
    else:
        categoria = "outros"

    return {
        "valido": True,
        "categoria": categoria,
        "confianca": 0.91,
        "motivo": None,
    }


# ---------- Background Task ----------

async def processar_triagem_e_notificar(
    item_id: str,
    caminho_arquivo: str,
):
    """Roda em segundo plano: IA → ativar ou rejeitar → notificar."""
    print(f"[Background] Triagem do item {item_id}...")

    resultado = analisar_imagem_com_ia(caminho_arquivo)

    if not resultado["valido"]:
        print(f"[Background] Item {item_id} rejeitado pela IA.")
        rejeitar_item(item_id)
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        return

    # Ativa o item e dispara matches + WebSocket
    sucesso = ativar_item_e_notificar(item_id, resultado["categoria"])

    if sucesso:
        item = store.get(item_id)
        if item:
            coletores = listar_coletores()
            matches = find_matches(item, coletores)
            payload = {
                "evento": "novo_descarte_proximo",
                "item": {
                    "id": item.id,
                    "categoria": item.categoria,
                    "lat": item.lat,
                    "lng": item.lng,
                    "foto_url": item.foto_url,
                },
            }
            for match in matches:
                await gerenciador_notificacoes.enviar_alerta_individual(
                    match.coletor_id, payload
                )
        print(f"[Background] Item {item_id} aprovado e notificado.")
    else:
        print(f"[Background] Falha ao ativar item {item_id}.")


# ---------- Schemas ----------

class ColetorCreate(BaseModel):
    lat: float
    lng: float
    interesses: List[str]
    raio_km: float = 3.0
    coletor_id: Optional[str] = None


class ItemCreate(BaseModel):
    foto_url: str
    categoria: str
    lat: float
    lng: float
    validade_horas: int = Field(default=48, ge=1, le=168)


class AceiteRequest(BaseModel):
    item_id: str
    coletor_id: str


class RequisicaoRota(BaseModel):
    coletor_lat: float
    coletor_lng: float
    item_ids: List[str]


class RequisicaoConclusao(BaseModel):
    item_id: str
    coletor_id: str


class ItemResponse(BaseModel):
    id: str
    foto_url: str
    categoria: str
    lat: float
    lng: float
    status: str

    @classmethod
    def from_model(cls, item: Item) -> "ItemResponse":
        return cls(
            id=item.id,
            foto_url=item.foto_url,
            categoria=item.categoria,
            lat=item.lat,
            lng=item.lng,
            status=item.status,
        )


# ---------- Endpoints HTTP ----------

@app.get("/")
def root():
    return {
        "app": "Tinder do Descarte",
        "status": "online",
        "version": "0.7.0",
        "docs": "/docs",
        "websocket": "/notificacoes/conectar/{coletor_id}",
    }


@app.post("/coletores", summary="Cadastrar coletor")
def criar_coletor(dados: ColetorCreate):
    cid = cadastrar_coletor(
        lat=dados.lat,
        lng=dados.lng,
        interesses=dados.interesses,
        raio_km=dados.raio_km,
        coletor_id=dados.coletor_id,
    )
    return {"coletor_id": cid}


@app.post("/itens", summary="Publicar item (com URL de foto já existente)")
async def criar_item(dados: ItemCreate):
    item_id = publicar_item(
        foto_url=dados.foto_url,
        categoria=dados.categoria,
        lat=dados.lat,
        lng=dados.lng,
        validade_horas=dados.validade_horas,
    )

    item = store.get(item_id)
    if item:
        coletores = listar_coletores()
        matches = find_matches(item, coletores)
        payload = {
            "evento": "novo_descarte_proximo",
            "item": {
                "id": item.id,
                "categoria": item.categoria,
                "lat": item.lat,
                "lng": item.lng,
                "foto_url": item.foto_url,
            },
        }
        for match in matches:
            await gerenciador_notificacoes.enviar_alerta_individual(
                match.coletor_id, payload
            )

    return {"item_id": item_id}


@app.post(
    "/itens/publicar-com-foto",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Publicar item com upload (processamento em background)",
)
async def publicar_item_com_foto(
    background_tasks: BackgroundTasks,
    latitude: float = Form(...),
    longitude: float = Form(...),
    file: UploadFile = File(...),
    validade_horas: int = Form(48),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo sem nome.",
        )

    extensao = file.filename.split(".")[-1].lower()
    if extensao not in ["jpg", "jpeg", "png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas imagens JPG ou PNG são permitidas.",
        )

    novo_nome = f"{uuid.uuid4()}.{extensao}"
    caminho_final = os.path.join(UPLOAD_DIR, novo_nome)

    content = await file.read()
    with open(caminho_final, "wb") as buffer:
        buffer.write(content)

    foto_url = f"/static/uploads/{novo_nome}"

    # Cria o item já no banco, mas ainda invisível no mapa
    item_id = criar_item_temporario(
        foto_url=foto_url,
        lat=latitude,
        lng=longitude,
        validade_horas=validade_horas,
    )

    # Agenda a triagem + notificação para rodar depois da resposta
    background_tasks.add_task(
        processar_triagem_e_notificar,
        item_id,
        caminho_final,
    )

    return {
        "mensagem": "Upload recebido. O item está em triagem.",
        "item_id": item_id,
        "status_atual": "processando",
        "foto_url": foto_url,
    }


@app.post("/matches/aceitar", summary="Coletor aceita um item")
def aceitar(dados: AceiteRequest):
    sucesso = aceitar_match(dados.item_id, dados.coletor_id)
    if not sucesso:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível aceitar o item (já aceito, expirado ou inexistente)",
        )
    return {"ok": True, "item_id": dados.item_id}


@app.get("/itens/proximos", summary="Listar itens próximos")
def itens_proximos(lat: float, lng: float, raio_km: float = 5.0):
    itens = listar_itens_proximos(lat, lng, raio_km)
    return [ItemResponse.from_model(i) for i in itens]


@app.post("/coletas/otimizar-rota", summary="Otimizar ordem de coleta (Nearest Neighbor)")
async def otimizar_rota_coleta(dados: RequisicaoRota):
    if not dados.item_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A lista de IDs de itens não pode estar vazia.",
        )

    itens_para_coleta = []
    for item_id in dados.item_ids:
        item = store.get(item_id)
        if item and item.status in ("ativo", "aceito"):
            itens_para_coleta.append({
                "id": item.id,
                "foto_url": item.foto_url,
                "categoria": item.categoria,
                "lat": item.lat,
                "lng": item.lng,
                "status": item.status,
            })

    if not itens_para_coleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum dos itens informados foi localizado ou está ativo.",
        )

    sequencia = otimizador_rotas.planejar_rota(
        lat_partida=dados.coletor_lat,
        lng_partida=dados.coletor_lng,
        itens=itens_para_coleta,
    )

    distancia_total = sum(
        item.get("distancia_da_parada_anterior_km", 0) for item in sequencia
    )

    return {
        "mensagem": "Rota gerada e otimizada com sucesso",
        "origem_coletor": {
            "latitude": dados.coletor_lat,
            "longitude": dados.coletor_lng,
        },
        "total_paradas": len(sequencia),
        "distancia_total_estimada_km": round(distancia_total, 2),
        "sequencia_da_rota": sequencia,
    }


@app.post("/coletas/concluir", summary="Concluir coleta e gerar pontos verdes")
def concluir_descarte(dados: RequisicaoConclusao):
    resultado = gerenciador_historico.concluir_coleta(dados.item_id, dados.coletor_id)

    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["erro"])

    return resultado


@app.get("/coletas/historico", summary="Listar coletas já concluídas")
def consultar_historico(limite: int = 50):
    return gerenciador_historico.listar_historico(limite)


@app.get("/coletas/pontos/{coletor_id}", summary="Total de pontos verdes de um coletor")
def consultar_pontos_coletor(coletor_id: str):
    pontos = gerenciador_historico.total_pontos_por_coletor(coletor_id)
    return {
        "coletor_id": coletor_id,
        "total_moedas_verdes": pontos,
    }


@app.get("/impacto/global", summary="Painel de impacto ambiental global")
def impacto_global():
    return calculadora_impacto.calcular_impacto_global()


@app.get("/impacto/coletor/{coletor_id}", summary="Impacto ambiental de um coletor")
def impacto_por_coletor(coletor_id: str):
    return calculadora_impacto.calcular_impacto_por_coletor(coletor_id)


@app.post("/manutencao/limpar-expirados", summary="Limpar itens expirados")
def limpar():
    quantidade = limpar_itens_expirados()
    return {"itens_expirados": quantidade}


@app.get("/status")
def status_app():
    return {
        "itens_ativos": len(store.listar_ativos()),
        "coletores_cadastrados": len(listar_coletores()),
        "coletores_online": gerenciador_notificacoes.coletores_online(),
    }


# ---------- WebSocket de notificações em tempo real ----------

@app.websocket("/notificacoes/conectar/{coletor_id}")
async def websocket_endpoint(websocket: WebSocket, coletor_id: str):
    await gerenciador_notificacoes.conectar(coletor_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"ok:{data}")
    except WebSocketDisconnect:
        gerenciador_notificacoes.desconectar(coletor_id)
    except Exception as e:
        print(f"Erro no canal do coletor {coletor_id}: {e}")
        gerenciador_notificacoes.desconectar(coletor_id)
