from typing import List
from .models import Item


class ItemStore:
    def __init__(self):
        self.items = {}  # id -> Item

    def add(self, item: Item) -> None:
        # TODO: salvar o item e agendar expiração
        pass

    def get_active_near(self, lat: float, lng: float, raio_km: float) -> List[Item]:
        # TODO: retornar apenas itens ativos dentro do raio
        pass

    def expire_old(self) -> int:
        # TODO: marcar como expirado e retornar quantos sumiram
        pass
