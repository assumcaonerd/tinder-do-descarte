from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from .models import Item, Coletor, Match
from .store import ItemStore
from .proximity import find_matches
from .notify import notify_coletor, notification_service


# Instâncias globais simples (em produção virariam banco de dados)
store = ItemStore()
coletores: dict[str, Coletor] = {}


def cadastrar_coletor(
    lat: float,
    lng: float,
    interesses: List[str],
    raio_km: float = 3.0,
    coletor_id: Optional[str] = None,
) -> str:
    """Cadastra ou atualiza um coletor e retorna o id."""
    cid = coletor_id or str(uuid4())
    coletores[cid] = Coletor(
        id=cid,
        lat=lat,
        lng=lng,
        interesses=interesses,
        raio_km=raio_km,
    )
    return cid


def publicar_item(
    foto_url: str,
    categoria: str,
    lat: float,
    lng: float,
    validade_horas: int = 48,
) -> str:
    """Publica um novo item, encontra matches e dispara notificações.
    Retorna o id do item criado.
    """
    item_id = str(uuid4())
    agora = datetime.utcnow()

    item = Item(
        id=item_id,
        foto_url=foto_url,
        categoria=categoria,
        lat=lat,
        lng=lng,
        created_at=agora,
        expires_at=agora + timedelta(hours=validade_horas),
        status="ativo",
    )

    store.add(item)

    # Encontra coletores próximos e com interesse
    matches = find_matches(item, list(coletores.values()))

    for match in matches:
        notify_coletor(match.coletor_id, item, match.distancia_km)

    return item_id


def aceitar_match(item_id: str, coletor_id: str) -> bool:
    """Coletor aceita coletar o item.
    Retorna True se o aceite foi bem-sucedido.
    """
    sucesso = store.marcar_aceito(item_id)

    if sucesso:
        # Aqui no futuro avisamos o doador
        print(f"[ACEITE] Coletor {coletor_id} aceitou o item {item_id}")
        notification_service.marcar_como_lida(coletor_id, item_id)

    return sucesso


def listar_itens_proximos(lat: float, lng: float, raio_km: float = 5.0) -> List[Item]:
    """Útil para o app do coletor ver o que tem perto."""
    return store.get_active_near(lat, lng, raio_km)


def limpar_itens_expirados() -> int:
    """Deve ser chamado periodicamente (cron ou background task)."""
    return store.expire_old()
