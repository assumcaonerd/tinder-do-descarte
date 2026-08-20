from datetime import datetime
from typing import List, Dict

from .db import get_connection, init_db


def criar_tabela_historico() -> None:
    """Cria a tabela de histórico se ela não existir."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_coletas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            categoria TEXT NOT NULL,
            foto_url TEXT,
            coletor_id TEXT NOT NULL,
            pontos_verdes INTEGER NOT NULL,
            data_conclusao TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


class GerenciadorHistorico:
    def __init__(self):
        criar_tabela_historico()

    def concluir_coleta(self, item_id: str, coletor_id: str) -> dict:
        """
        Move o item do estado ativo/aceito para o histórico.
        Calcula pontos verdes e remove o item do mapa público.
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, categoria, foto_url, status FROM itens WHERE id = ?",
                (item_id,),
            )
            row = cursor.fetchone()

            if not row:
                return {
                    "sucesso": False,
                    "erro": "Item não encontrado, já coletado ou expirado.",
                }

            if row["status"] not in ("ativo", "aceito"):
                return {
                    "sucesso": False,
                    "erro": f"Item com status '{row['status']}' não pode ser concluído.",
                }

            # Pontuação por categoria
            tabela_pontos = {
                "eletronico": 20,
                "metal": 15,
                "madeira": 10,
            }
            categoria = row["categoria"].lower()
            pontos = tabela_pontos.get(categoria, 10)

            agora = datetime.utcnow().isoformat()

            cursor.execute(
                """
                INSERT INTO historico_coletas
                (item_id, categoria, foto_url, coletor_id, pontos_verdes, data_conclusao)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (row["id"], row["categoria"], row["foto_url"], coletor_id, pontos, agora),
            )

            # Marca como concluído (em vez de DELETE, preserva a linha se quiser auditoria futura)
            cursor.execute(
                "UPDATE itens SET status = 'concluido' WHERE id = ?",
                (item_id,),
            )

            conn.commit()

            return {
                "sucesso": True,
                "dados": {
                    "item_id": item_id,
                    "categoria": row["categoria"],
                    "coletor_id": coletor_id,
                    "pontos_verdes": pontos,
                    "data_conclusao": agora,
                },
            }
        except Exception as e:
            conn.rollback()
            return {"sucesso": False, "erro": str(e)}
        finally:
            conn.close()

    def listar_historico(self, limite: int = 50) -> List[Dict]:
        """Retorna os últimos descartes concluídos."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM historico_coletas
            ORDER BY data_conclusao DESC
            LIMIT ?
            """,
            (limite,),
        )
        linhas = cursor.fetchall()
        conn.close()
        return [dict(linha) for linha in linhas]

    def total_pontos_por_coletor(self, coletor_id: str) -> int:
        """Soma os pontos verdes gerados por um coletor."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(pontos_verdes) FROM historico_coletas WHERE coletor_id = ?",
            (coletor_id,),
        )
        resultado = cursor.fetchone()[0]
        conn.close()
        return resultado if resultado is not None else 0


gerenciador_historico = GerenciadorHistorico()
