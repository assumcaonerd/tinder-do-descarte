from .models import Item
from .store import ItemStore
from .proximity import find_matches
from .notify import notify_coletor


def publicar_item(foto_url: str, categoria: str, lat: float, lng: float) -> str:
    # TODO: criar Item, salvar, disparar matches e retornar o id
    pass


def aceitar_match(match_id: str, coletor_id: str) -> bool:
    # TODO: marcar item como aceito e avisar o doador
    pass
