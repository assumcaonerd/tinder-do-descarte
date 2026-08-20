import os
import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .models import Item, Coletor
from .proximity import haversine


# Permite sobrescrever o caminho via variável de ambiente (útil no Docker)
_default_path = Path(__file__).parent.parent / "tinder_descarte.db"
DB_PATH = Path(os.getenv("DB_PATH", str(_default_path)))


def get_connection() -> sqlite3.Connection:
    # Garante que o diretório do banco exista
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Cria as tabelas se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id TEXT PRIMARY KEY,
            foto_url TEXT NOT NULL,
            categoria TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ativo'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coletores (
            id TEXT PRIMARY KEY,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            interesses TEXT NOT NULL,
            raio_km REAL NOT NULL DEFAULT 3.0
        )
    """)

    conn.commit()
    conn.close()


class SQLiteItemStore:
    """Store de itens usando SQLite."""

    def __init__(self):
        init_db()

    def add(self, item: Item) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO itens
            (id, foto_url, categoria, lat, lng, created_at, expires_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                item.foto_url,
                item.categoria,
                item.lat,
                item.lng,
                item.created_at.isoformat(),
                item.expires_at.isoformat(),
                item.status,
            ),
        )
        conn.commit()
        conn.close()

    def get(self, item_id: str) -> Optional[Item]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itens WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Item(
            id=row["id"],
            foto_url=row["foto_url"],
            categoria=row["categoria"],
            lat=row["lat"],
            lng=row["lng"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            status=row["status"],
        )

    def atualizar_status(
        self,
        item_id: str,
        status: str,
        categoria: Optional[str] = None,
    ) -> bool:
        """Atualiza status (e opcionalmente a categoria) de um item."""
        conn = get_connection()
        cursor = conn.cursor()

        if categoria is not None:
            cursor.execute(
                "UPDATE itens SET status = ?, categoria = ? WHERE id = ?",
                (status, categoria, item_id),
            )
        else:
            cursor.execute(
                "UPDATE itens SET status = ? WHERE id = ?",
                (status, item_id),
            )

        sucesso = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return sucesso

    def get_active_near(self, lat: float, lng: float, raio_km: float) -> List[Item]:
        agora = datetime.utcnow().isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM itens
            WHERE status = 'ativo' AND expires_at >= ?
            """,
            (agora,),
        )
        rows = cursor.fetchall()
        conn.close()

        resultado = []
        for row in rows:
            dist = haversine(lat, lng, row["lat"], row["lng"])
            if dist <= raio_km:
                resultado.append(
                    Item(
                        id=row["id"],
                        foto_url=row["foto_url"],
                        categoria=row["categoria"],
                        lat=row["lat"],
                        lng=row["lng"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                        expires_at=datetime.fromisoformat(row["expires_at"]),
                        status=row["status"],
                    )
                )
        return resultado

    def expire_old(self) -> int:
        agora = datetime.utcnow().isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE itens
            SET status = 'expirado'
            WHERE status = 'ativo' AND expires_at < ?
            """,
            (agora,),
        )
        quantidade = cursor.rowcount
        conn.commit()
        conn.close()
        return quantidade

    def marcar_aceito(self, item_id: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE itens
            SET status = 'aceito'
            WHERE id = ? AND status = 'ativo'
            """,
            (item_id,),
        )
        sucesso = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return sucesso

    def listar_ativos(self) -> List[Item]:
        agora = datetime.utcnow().isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM itens
            WHERE status = 'ativo' AND expires_at >= ?
            """,
            (agora,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            Item(
                id=row["id"],
                foto_url=row["foto_url"],
                categoria=row["categoria"],
                lat=row["lat"],
                lng=row["lng"],
                created_at=datetime.fromisoformat(row["created_at"]),
                expires_at=datetime.fromisoformat(row["expires_at"]),
                status=row["status"],
            )
            for row in rows
        ]


def salvar_coletor(coletor: Coletor) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    interesses_str = ",".join(coletor.interesses)
    cursor.execute(
        """
        INSERT OR REPLACE INTO coletores (id, lat, lng, interesses, raio_km)
        VALUES (?, ?, ?, ?, ?)
        """,
        (coletor.id, coletor.lat, coletor.lng, interesses_str, coletor.raio_km),
    )
    conn.commit()
    conn.close()


def listar_coletores() -> List[Coletor]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coletores")
    rows = cursor.fetchall()
    conn.close()

    return [
        Coletor(
            id=row["id"],
            lat=row["lat"],
            lng=row["lng"],
            interesses=row["interesses"].split(",") if row["interesses"] else [],
            raio_km=row["raio_km"],
        )
        for row in rows
    ]
