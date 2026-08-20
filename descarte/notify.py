from datetime import datetime
from typing import List, Dict
from .models import Item


class NotificationService:
    """Serviço simples de notificações.

    Por enquanto guarda as notificações em memória.
    Depois pode ser trocado por Firebase Cloud Messaging, OneSignal ou outro provedor de push.
    """

    def __init__(self):
        self._fila: List[Dict] = []

    def notify_coletor(self, coletor_id: str, item: Item, distancia: float) -> None:
        notificacao = {
            "coletor_id": coletor_id,
            "item_id": item.id,
            "categoria": item.categoria,
            "distancia_km": distancia,
            "mensagem": f"Novo item disponível a {distancia:.1f} km: {item.categoria}",
            "enviado_em": datetime.utcnow().isoformat() + "Z",
            "lida": False,
        }
        self._fila.append(notificacao)
        print(f"[PUSH] → Coletor {coletor_id}: {notificacao['mensagem']}")

    def get_notificacoes(self, coletor_id: str, apenas_nao_lidas: bool = True) -> List[Dict]:
        resultado = [
            n for n in self._fila
            if n["coletor_id"] == coletor_id and (not apenas_nao_lidas or not n["lida"])
        ]
        return resultado

    def marcar_como_lida(self, coletor_id: str, item_id: str) -> bool:
        for n in self._fila:
            if n["coletor_id"] == coletor_id and n["item_id"] == item_id:
                n["lida"] = True
                return True
        return False


# Instância global para facilitar o uso no início do projeto
notification_service = NotificationService()


def notify_coletor(coletor_id: str, item: Item, distancia: float) -> None:
    """Função de conveniência que usa o serviço global."""
    notification_service.notify_coletor(coletor_id, item, distancia)
