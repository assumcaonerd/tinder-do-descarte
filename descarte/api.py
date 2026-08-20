from typing import List, Optional
from fastapi import FastAPI, HTTPException
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


app = FastAPI(
    title="Tinder do Descarte",
    description="API para descarte responsável de resíduos volumosos",
    version="0.1.0",
)


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


# ---------- Endpoints ----------

@app.get("/")
def root():
    return {
        "app": "Tinder do Descarte",
        "status": "online",
        "docs": "/docs",
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


@app.post("/itens", summary="Publicar item para descarte")
def criar_item(dados: ItemCreate):
    item_id = publicar_item(
        foto_url=dados.foto_url,
        categoria=dados.categoria,
        lat=dados.lat,
        lng=dados.lng,
        validade_horas=dados.validade_horas,
    )
    return {"item_id": item_id}


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


@app.post("/manutencao/limpar-expirados", summary="Limpar itens expirados")
def limpar():
    quantidade = limpar_itens_expirados()
    return {"itens_expirados": quantidade}


@app.get("/status")
def status():
    return {
        "itens_ativos": len(store.listar_ativos()),
        "coletores_cadastrados": len(listar_coletores()),
    }
