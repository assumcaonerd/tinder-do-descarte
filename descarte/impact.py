from typing import Dict
from .db import get_connection


class CalculadoraImpactoAmbiental:
    def __init__(self):
        # Fatores médios estimativos por categoria
        # peso_medio_kg: massa aproximada do item
        # co2_poupado_por_kg: kg de CO₂ evitados ao reutilizar/reciclar 1 kg do material
        self.fatores_conversao = {
            "madeira": {"peso_medio_kg": 25.0, "co2_poupado_por_kg": 0.5},
            "metal": {"peso_medio_kg": 15.0, "co2_poupado_por_kg": 1.2},
            "eletronico": {"peso_medio_kg": 8.0, "co2_poupado_por_kg": 2.5},
            "outros": {"peso_medio_kg": 10.0, "co2_poupado_por_kg": 0.4},
        }

    def _calcular(self, categorias: list) -> Dict:
        total_itens = len(categorias)
        total_peso_kg = 0.0
        total_co2_kg = 0.0

        for categoria in categorias:
            cat = (categoria or "outros").lower()
            fatores = self.fatores_conversao.get(cat, self.fatores_conversao["outros"])
            peso = fatores["peso_medio_kg"]
            total_peso_kg += peso
            total_co2_kg += peso * fatores["co2_poupado_por_kg"]

        return {
            "total_descartes_concluidos": total_itens,
            "massa_total_desviada_aterros_kg": round(total_peso_kg, 2),
            "massa_total_desviada_aterros_toneladas": round(total_peso_kg / 1000, 3),
            "co2_total_poupado_kg": round(total_co2_kg, 2),
            "equivalencia_arvores_salvas_ano": round(total_co2_kg / 15.0, 1),
        }

    def calcular_impacto_global(self) -> Dict:
        """Impacto de todos os descartes já concluídos."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT categoria FROM historico_coletas")
        rows = cursor.fetchall()
        conn.close()

        categorias = [row["categoria"] for row in rows]
        return self._calcular(categorias)

    def calcular_impacto_por_coletor(self, coletor_id: str) -> Dict:
        """Impacto gerado por um coletor específico."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT categoria FROM historico_coletas WHERE coletor_id = ?",
            (coletor_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        categorias = [row["categoria"] for row in rows]
        resultado = self._calcular(categorias)
        resultado["coletor_id"] = coletor_id
        return resultado


calculadora_impacto = CalculadoraImpactoAmbiental()
