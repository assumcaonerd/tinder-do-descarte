from typing import List, Dict
from .proximity import haversine


class OtimizadorDeRotas:
    def planejar_rota(
        self,
        lat_partida: float,
        lng_partida: float,
        itens: List[Dict],
    ) -> List[Dict]:
        """
        Ordena os itens usando o algoritmo do Vizinho Mais Próximo (Nearest Neighbor).

        Cada item da lista de entrada deve conter pelo menos:
        - id
        - lat (ou latitude)
        - lng (ou longitude)

        Retorna a lista reordenada com o campo adicional:
        - distancia_da_parada_anterior_km
        """
        if not itens:
            return []

        rota_ordenada = []
        itens_restantes = [dict(item) for item in itens]  # cópia rasa

        lat_atual = lat_partida
        lng_atual = lng_partida

        while itens_restantes:
            proximo_item = None
            menor_distancia = float("inf")

            for item in itens_restantes:
                item_lat = item.get("latitude") or item.get("lat")
                item_lng = item.get("longitude") or item.get("lng")

                if item_lat is None or item_lng is None:
                    continue

                dist = haversine(lat_atual, lng_atual, item_lat, item_lng)

                if dist < menor_distancia:
                    menor_distancia = dist
                    proximo_item = item

            if proximo_item is None:
                break

            itens_restantes.remove(proximo_item)
            proximo_item["distancia_da_parada_anterior_km"] = round(menor_distancia, 2)
            rota_ordenada.append(proximo_item)

            lat_atual = proximo_item.get("latitude") or proximo_item.get("lat")
            lng_atual = proximo_item.get("longitude") or proximo_item.get("lng")

        return rota_ordenada


otimizador_rotas = OtimizadorDeRotas()
