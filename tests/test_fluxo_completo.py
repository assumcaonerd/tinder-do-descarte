"""
Teste E2E do fluxo completo do Tinder do Descarte.

Cobre:
1. Registro e login (doador + coletor)
2. Cadastro de localização do coletor
3. Publicação com upload (202 + background)
4. Aceite e otimização de rota
5. Conclusão da coleta
6. Validação de impacto ambiental
"""

import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from descarte.api import app
from descarte.db import DB_PATH, init_db
from descarte.auth import criar_tabela_usuarios
from descarte.historico import criar_tabela_historico


class TestFluxoCompleto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Banco limpo para o teste
        if DB_PATH.exists():
            DB_PATH.unlink()
        init_db()
        criar_tabela_usuarios()
        criar_tabela_historico()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if DB_PATH.exists():
            DB_PATH.unlink()

    def test_ciclo_de_vida_completo(self):
        # -------------------------------------------------
        # 1. Cadastro e login do DOADOR
        # -------------------------------------------------
        r = self.client.post(
            "/auth/registro",
            json={
                "email": "doador_e2e@email.com",
                "senha": "senha123",
                "role": "doador",
                "nome": "Doador Teste",
            },
        )
        self.assertEqual(r.status_code, 200)

        r = self.client.post(
            "/auth/login",
            data={
                "username": "doador_e2e@email.com",
                "password": "senha123",
            },
        )
        self.assertEqual(r.status_code, 200)
        token_doador = r.json()["access_token"]
        headers_doador = {"Authorization": f"Bearer {token_doador}"}

        # -------------------------------------------------
        # 2. Cadastro e login do COLETOR
        # -------------------------------------------------
        r = self.client.post(
            "/auth/registro",
            json={
                "email": "coletor_e2e@email.com",
                "senha": "senha123",
                "role": "coletor",
                "nome": "Cooperativa E2E",
            },
        )
        self.assertEqual(r.status_code, 200)

        r = self.client.post(
            "/auth/login",
            data={
                "username": "coletor_e2e@email.com",
                "password": "senha123",
            },
        )
        self.assertEqual(r.status_code, 200)
        token_coletor = r.json()["access_token"]
        coletor_id = r.json()["usuario_id"]
        headers_coletor = {"Authorization": f"Bearer {token_coletor}"}

        # Localização do coletor
        r = self.client.post(
            "/coletores",
            json={
                "lat": -20.3155,
                "lng": -40.3128,
                "interesses": ["madeira", "eletronico", "metal", "outros"],
                "raio_km": 10.0,
            },
            headers=headers_coletor,
        )
        self.assertEqual(r.status_code, 200)

        # -------------------------------------------------
        # 3. Publicação com upload (assíncrona)
        # -------------------------------------------------
        foto_fake = ("sofa_madeira.png", b"fake_image_content", "image/png")

        r = self.client.post(
            "/itens/publicar-com-foto",
            data={
                "latitude": -20.3160,
                "longitude": -40.3130,
                "validade_horas": 48,
            },
            files={"file": foto_fake},
            headers=headers_doador,
        )
        self.assertEqual(r.status_code, 202)
        dados = r.json()
        item_id = dados["item_id"]
        self.assertEqual(dados["status_atual"], "processando")

        # Aguarda a BackgroundTask (triagem + ativação)
        time.sleep(1.5)

        # -------------------------------------------------
        # 4. Item deve aparecer na listagem de próximos
        # -------------------------------------------------
        r = self.client.get(
            "/itens/proximos",
            params={"lat": -20.3155, "lng": -40.3128, "raio_km": 5.0},
        )
        self.assertEqual(r.status_code, 200)
        itens = r.json()
        ids = [i["id"] for i in itens]
        self.assertIn(item_id, ids)

        # -------------------------------------------------
        # 5. Coletor aceita o item
        # -------------------------------------------------
        r = self.client.post(
            "/matches/aceitar",
            json={"item_id": item_id},
            headers=headers_coletor,
        )
        self.assertEqual(r.status_code, 200)

        # -------------------------------------------------
        # 6. Otimização de rota
        # -------------------------------------------------
        r = self.client.post(
            "/coletas/otimizar-rota",
            json={
                "coletor_lat": -20.3155,
                "coletor_lng": -40.3128,
                "item_ids": [item_id],
            },
            headers=headers_coletor,
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["total_paradas"], 1)

        # -------------------------------------------------
        # 7. Conclusão da coleta
        # -------------------------------------------------
        r = self.client.post(
            "/coletas/concluir",
            json={"item_id": item_id},
            headers=headers_coletor,
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["sucesso"])

        # Item não deve mais aparecer como ativo
        r = self.client.get(
            "/itens/proximos",
            params={"lat": -20.3155, "lng": -40.3128, "raio_km": 5.0},
        )
        ids_depois = [i["id"] for i in r.json()]
        self.assertNotIn(item_id, ids_depois)

        # -------------------------------------------------
        # 8. Impacto ambiental deve refletir a coleta
        # -------------------------------------------------
        r = self.client.get("/impacto/global")
        self.assertEqual(r.status_code, 200)
        impacto = r.json()
        self.assertGreaterEqual(impacto["total_descartes_concluidos"], 1)
        self.assertGreater(impacto["massa_total_desviada_aterros_kg"], 0)

        # Pontos do coletor
        r = self.client.get(f"/coletas/pontos/{coletor_id}")
        self.assertEqual(r.status_code, 200)
        self.assertGreater(r.json()["total_moedas_verdes"], 0)


if __name__ == "__main__":
    unittest.main()
