import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .main import (
    cadastrar_coletor,
    publicar_item,
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


app = FastAPI(
    title="Tinder do Descarte",
    description="API para descarte responsável de resíduos volumosos",
    version="0.4.0",
)

# Diretório de uploads
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve os arquivos estáticos (fotos)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------- Simulação de IA de triagem ----------

def analisar_imagem_com_ia(file_path: str) -> dict:
    """
    Simula uma chamada de visão computacional.
    Em produção aqui entraria um modelo real (CLIP, YOLO, etc.).
    """
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
        "version": "0.4.0",
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


@app.post("/itens/publicar-com-foto", summary="Publicar item com upload de foto + validação de IA")
async def publicar_item_com_foto(
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

    resultado_ia = analisar_imagem_com_ia(caminho_final)

    if not resultado_ia["valido"]:
        os.remove(caminho_final)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado_ia["motivo"] or "Item rejeitado pela análise de imagem.",
        )

    foto_url = f"/static/uploads/{novo_nome}"

    item_id = publicar_item(
        foto_url=foto_url,
        categoria=resultado_ia["categoria"],
        lat=latitude,
        lng=longitude,
        validade_horas=validade_horas,
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

    return {
        "mensagem": "Item publicado e coletores da região alertados",
        "item_id": item_id,
        "foto_url": foto_url,
        "categoria_detectada": resultado_ia["categoria"],
        "confianca_ia": resultado_ia["confianca"],
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
        if item:
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


@app.post("/manutencao/limpar-expirados", summary="Limpar itens expirados")
def limpar():
    quantidade = limpar_itens_expirados()
    return {"itens_expirados": quantidade}


@app.get("/status")
def status():
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
