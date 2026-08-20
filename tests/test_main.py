import unittest
from descarte.main import (
    cadastrar_coletor,
    publicar_item,
    aceitar_match,
    listar_itens_proximos,
    limpar_itens_expirados,
    store,
    coletores,
)


class TestMainFlow(unittest.TestCase):

    def setUp(self):
        # Limpa o estado entre os testes
        store.items.clear()
        coletores.clear()

    def test_fluxo_completo(self):
        # Cadastra coletor
        cid = cadastrar_coletor(
            lat=-20.3155,
            lng=-40.3128,
            interesses=["madeira", "eletronico"],
            raio_km=5.0,
        )
        self.assertIn(cid, coletores)

        # Publica item próximo
        item_id = publicar_item(
            foto_url="http://exemplo.com/sofa.jpg",
            categoria="madeira",
            lat=-20.3170,
            lng=-40.3110,
        )

        self.assertIsNotNone(store.get(item_id))

        # Deve aparecer na listagem
        proximos = listar_itens_proximos(-20.3155, -40.3128, raio_km=5.0)
        self.assertEqual(len(proximos), 1)
        self.assertEqual(proximos[0].id, item_id)

        # Aceita
        sucesso = aceitar_match(item_id, cid)
        self.assertTrue(sucesso)
        self.assertEqual(store.get(item_id).status, "aceito")

        # Depois de aceito, não deve mais aparecer como ativo
        proximos_depois = listar_itens_proximos(-20.3155, -40.3128, raio_km=5.0)
        self.assertEqual(len(proximos_depois), 0)


if __name__ == "__main__":
    unittest.main()
