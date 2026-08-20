from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Item:
    id: str
    foto_url: str
    categoria: str          # "madeira", "eletronico", "metal", etc.
    lat: float
    lng: float
    created_at: datetime
    expires_at: datetime
    status: str = "ativo"   # ativo | aceito | expirado


@dataclass
class Coletor:
    id: str
    lat: float
    lng: float
    interesses: List[str]
    raio_km: float = 3.0


@dataclass
class Match:
    item_id: str
    coletor_id: str
    distancia_km: float
    status: str = "pendente"  # pendente | aceito | rejeitado
