import unittest
from descarte.proximity import haversine, find_matches
from descarte.models import Item, Coletor
from datetime import datetime, timedelta


class TestProximity(unittest.TestCase):

    def test_haversine_mesma_posicao(self):
        dist = haversine(-20.3155, -40.3128, -20.3155, -40.3128)
        self.assertAlmostEqual(dist, 0.0, places=5)

    def test_haversine_distancia_conhecida(self):
        # Distância aproximada entre dois pontos próximos em Vitória
        dist = haversine(-20.3155, -40.3128, -20.3200, -40.3100)
        self.assertGreater(dist, 0.4)
        self.assertLess(dist, 0.8)

    def test_find_matches_dentro_do_raio(self):
        item = Item(
            id="item1",
            foto_url="http://exemplo.com/sofa.jpg",
            categoria="madeira",
            lat=-20.3155,
            lng=-40.3128,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=48),
        )

        coletor_perto = Coletor(
            id="c1",
            lat=-20.3160,
            lng=-40.3130,
            interesses=["madeira"],
            raio_km=3.0,
        )

        coletor_longe = Coletor(
            id="c2",
            lat=-20.4000,
            lng=-40.4000,
            interesses=["madeira"],
            raio_km=3.0,
        )

        matches = find_matches(item, [coletor_perto, coletor_longe])

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].coletor_id, "c1")

    def test_find_matches_filtra_por_interesse(self):
        item = Item(
            id="item2",
            foto_url="http://exemplo.com/tv.jpg",
            categoria="eletronico",
            lat=-20.3155,
            lng=-40.3128,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=48),
        )

        coletor_sem_interesse = Coletor(
            id="c3",
            lat=-20.3160,
            lng=-40.3130,
            interesses=["madeira"],
            raio_km=5.0,
        )

        matches = find_matches(item, [coletor_sem_interesse])
        self.assertEqual(len(matches), 0)


if __name__ == "__main__":
    unittest.main()
