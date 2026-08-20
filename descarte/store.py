from datetime import datetime
from typing import List, Optional
from .models import Item
from .proximity import haversine


class ItemStore:
    def __init__(self):
        self.items: dict[str, Item] = {}

    def add(self, item: Item) -> None:
        """Adiciona um novo item ao store."""
        self.items[item.id] = item

    def get(self, item_id: str) -> Optional[Item]:
        return self.items.get(item_id)

    def get_active_near(self, lat: float, lng: float, raio_km: float) -> List[Item]:
        """Retorna apenas itens ativos que estão dentro do raio informado."""
        agora = datetime.utcnow()
        resultado = []

        for item in self.items.values():
            if item.status != "ativo":
                continue
            if item.expires_at < agora:
                item.status = "expirado"
                continue

            distancia = haversine(lat, lng, item.lat, item.lng)
            if distancia <= raio_km:
                resultado.append(item)

        return resultado

    def expire_old(self) -> int:
        """Marca como expirado todos os itens que passaram da data de validade.
        Retorna a quantidade de itens que expiraram nesta execução.
        """
        agora = datetime.utcnow()
        expirados = 0

        for item in self.items.values():
            if item.status == "ativo" and item.expires_at < agora:
                item.status = "expirado"
                expirados += 1

        return expirados

    def marcar_aceito(self, item_id: str) -> bool:
        """Marca um item como aceito. Retorna True se conseguiu."""
        item = self.items.get(item_id)
        if item and item.status == "ativo":
            item.status = "aceito"
            return True
        return False

    def listar_ativos(self) -> List[Item]:
        """Retorna todos os itens ainda ativos (útil para debug)."""
        agora = datetime.utcnow()
        return [
            item for item in self.items.values()
            if item.status == "ativo" and item.expires_at >= agora
        ]
