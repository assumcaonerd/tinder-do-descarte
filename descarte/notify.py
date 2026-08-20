from datetime import datetime
from typing import List, Dict
from fastapi import WebSocket

from .models import Item


class NotificationService:
    """Serviço simples de notificações em memória (histórico)."""

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
        return [
            n for n in self._fila
            if n["coletor_id"] == coletor_id and (not apenas_nao_lidas or not n["lida"])
        ]

    def marcar_como_lida(self, coletor_id: str, item_id: str) -> bool:
        for n in self._fila:
            if n["coletor_id"] == coletor_id and n["item_id"] == item_id:
                n["lida"] = True
                return True
        return False


class GerenciadorNotificacoesTempoReal:
    """Gerenciador de conexões WebSocket para alertas em tempo real."""

    def __init__(self):
        self.conexoes_ativas: Dict[str, WebSocket] = {}

    async def conectar(self, coletor_id: str, websocket: WebSocket):
        """Aceita a conexão e registra o coletor como online."""
        await websocket.accept()
        self.conexoes_ativas[coletor_id] = websocket
        print(f"🔌 [WebSocket] Coletor {coletor_id} agora está ONLINE.")

    def desconectar(self, coletor_id: str):
        """Remove o coletor do dicionário de ativos."""
        if coletor_id in self.conexoes_ativas:
            del self.conexoes_ativas[coletor_id]
            print(f"❌ [WebSocket] Coletor {coletor_id} ficou OFFLINE.")

    async def enviar_alerta_individual(self, coletor_id: str, payload: dict):
        """Envia um JSON em tempo real se o coletor estiver conectado."""
        websocket = self.conexoes_ativas.get(coletor_id)
        if websocket:
            try:
                await websocket.send_json(payload)
                print(f"🔔 [Push] Alerta enviado para o coletor: {coletor_id}")
            except Exception:
                self.desconectar(coletor_id)

    def coletores_online(self) -> List[str]:
        return list(self.conexoes_ativas.keys())


# Instâncias globais
notification_service = NotificationService()
gerenciador_notificacoes = GerenciadorNotificacoesTempoReal()


def notify_coletor(coletor_id: str, item: Item, distancia: float) -> None:
    """Função de conveniência que usa o serviço de histórico."""
    notification_service.notify_coletor(coletor_id, item, distancia)
