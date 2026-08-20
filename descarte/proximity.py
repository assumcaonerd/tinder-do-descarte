from typing import List
from .models import Item, Coletor, Match


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    # TODO: calcular distância em km entre dois pontos
    pass


def find_matches(item: Item, coletores: List[Coletor]) -> List[Match]:
    # TODO: filtrar coletores por distância e interesses
    pass
