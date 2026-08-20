from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from .models import Item, Coletor
from .db import SQLiteItemStore, salvar_coletor, listar_coletores, init_db
from .proximity import find_matches
from .notify import notify_coletor, notification_service


# Garante que as tabelas existem
init_db()

# Usa o store com persistência em SQLite
store = SQLiteItemStore()


def cadastrar_coletor(
    lat: float,
    lng: float,
    interesses: List[str],
    raio_km: float = 3.0,
    coletor_id: Optional[str] = None,
) -> str:
    """Cadastra ou atualiza um coletor e retorna o id."""
    cid = coletor_id or str(uuid4())
    coletor = Coletor(
        id=cid,
        lat=lat,
        lng=lng,
        interesses=interesses,
        raio_km=raio_km,
    )
    salvar_coletor(coletor)
    return cid


def criar_item_temporario(
    foto_url: str,
    lat: float,
    lng: float,
    validade_horas: int = 48,
) -> str:
    """Cria item com status 'processando' (ainda não aparece no mapa)."""
    item_id = str(uuid4())
    agora = datetime.utcnow()

    item = Item(
        id=item_id,
        foto_url=foto_url,
        categoria="processando",
        lat=lat,
        lng=lng,
        created_at=agora,
        expires_at=agora + timedelta(hours=validade_horas),
        status="processando",
    )
    store.add(item)
    return item_id


def publicar_item(
    foto_url: str,
    categoria: str,
    lat: float,
    lng: float,
    validade_horas: int = 48,
) -> str:
    """Publica um novo item já ativo, encontra matches e dispara notificações."""
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

    coletores = listar_coletores()
    matches = find_matches(item, coletores)

    for match in matches:
        notify_coletor(match.coletor_id, item, match.distancia_km)

    return item_id


def ativar_item_e_notificar(item_id: str, categoria: str) -> bool:
    """Ativa um item que estava em processamento e dispara alertas."""
    sucesso = store.atualizar_status(item_id, status="ativo", categoria=categoria)
    if not sucesso:
        return False

    item = store.get(item_id)
    if not item:
        return False

    coletores = listar_coletores()
    matches = find_matches(item, coletores)

    for match in matches:
        notify_coletor(match.coletor_id, item, match.distancia_km)

    return True


def rejeitar_item(item_id: str) -> bool:
    """Marca item como rejeitado pela IA."""
    return store.atualizar_status(item_id, status="rejeitado")


def aceitar_match(item_id: str, coletor_id: str) -> bool:
    """Coletor aceita coletar o item."""
    sucesso = store.marcar_aceito(item_id)

    if sucesso:
        print(f"[ACEITE] Coletor {coletor_id} aceitou o item {item_id}")
        notification_service.marcar_como_lida(coletor_id, item_id)

    return sucesso


def listar_itens_proximos(lat: float, lng: float, raio_km: float = 5.0) -> List[Item]:
    """Lista apenas itens ativos próximos."""
    return store.get_active_near(lat, lng, raio_km)


def limpar_itens_expirados() -> int:
    """Deve ser chamado periodicamente."""
    return store.expire_old()
