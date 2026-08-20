import unittest
from datetime import datetime, timedelta
from descarte.store import ItemStore
from descarte.models import Item


class TestItemStore(unittest.TestCase):

    def setUp(self):
        self.store = ItemStore()

    def _criar_item(self, item_id="item1", horas_validade=48, status="ativo"):
        agora = datetime.utcnow()
        return Item(
            id=item_id,
            foto_url="http://exemplo.com/foto.jpg",
            categoria="madeira",
            lat=-20.3155,
            lng=-40.3128,
            created_at=agora,
            expires_at=agora + timedelta(hours=horas_validade),
            status=status,
        )

    def test_add_e_get(self):
        item = self._criar_item()
        self.store.add(item)
        recuperado = self.store.get("item1")
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.id, "item1")

    def test_get_active_near(self):
        item = self._criar_item()
        self.store.add(item)

        # Ponto bem próximo
        proximos = self.store.get_active_near(-20.3160, -40.3130, raio_km=2.0)
        self.assertEqual(len(proximos), 1)

        # Ponto longe
        longe = self.store.get_active_near(-20.5000, -40.5000, raio_km=2.0)
        self.assertEqual(len(longe), 0)

    def test_expire_old(self):
        item_expirado = self._criar_item(item_id="exp", horas_validade=-1)  # já passou
        self.store.add(item_expirado)

        quantidade = self.store.expire_old()
        self.assertEqual(quantidade, 1)
        self.assertEqual(self.store.get("exp").status, "expirado")

    def test_marcar_aceito(self):
        item = self._criar_item()
        self.store.add(item)

        sucesso = self.store.marcar_aceito("item1")
        self.assertTrue(sucesso)
        self.assertEqual(self.store.get("item1").status, "aceito")

        # Não deve aceitar de novo
        sucesso2 = self.store.marcar_aceito("item1")
        self.assertFalse(sucesso2)


if __name__ == "__main__":
    unittest.main()
