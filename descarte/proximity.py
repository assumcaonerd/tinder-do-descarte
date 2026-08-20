from typing import List
from math import radians, sin, cos, sqrt, atan2
from .models import Item, Coletor, Match


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calcula a distância em quilômetros entre dois pontos geográficos."""
    R = 6371.0  # raio médio da Terra em km

    lat1_rad = radians(lat1)
    lng1_rad = radians(lng1)
    lat2_rad = radians(lat2)
    lng2_rad = radians(lng2)

    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def find_matches(item: Item, coletores: List[Coletor]) -> List[Match]:
    """Retorna os coletores que estão dentro do raio e têm interesse na categoria do item."""
    matches = []

    for coletor in coletores:
        distancia = haversine(item.lat, item.lng, coletor.lat, coletor.lng)

        if distancia > coletor.raio_km:
            continue

        if item.categoria not in coletor.interesses and "*" not in coletor.interesses:
            continue

        matches.append(
            Match(
                item_id=item.id,
                coletor_id=coletor.id,
                distancia_km=round(distancia, 2),
                status="pendente",
            )
        )

    # ordena do mais próximo para o mais longe
    matches.sort(key=lambda m: m.distancia_km)
    return matches
