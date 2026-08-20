import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext

from .db import get_connection, init_db


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "troque-esta-chave-em-producao-tinder-descarte-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def criar_tabela_usuarios() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            nome TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_pura, senha_hash)


def criar_token_acesso(dados: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = dados.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def cadastrar_usuario(
    email: str,
    senha: str,
    role: str,
    nome: Optional[str] = None,
    usuario_id: Optional[str] = None,
) -> dict:
    from uuid import uuid4

    if role not in ("doador", "coletor"):
        raise ValueError("Role deve ser 'doador' ou 'coletor'")

    uid = usuario_id or str(uuid4())
    senha_hash = gerar_hash_senha(senha)
    agora = datetime.utcnow().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (id, email, senha_hash, role, nome, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (uid, email.lower().strip(), senha_hash, role, nome, agora),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e).upper():
            raise ValueError("E-mail já cadastrado")
        raise
    finally:
        conn.close()

    return {"id": uid, "email": email, "role": role, "nome": nome}


def autenticar_usuario(email: str, senha: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, senha_hash, role, nome FROM usuarios WHERE email = ?",
        (email.lower().strip(),),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    if not verificar_senha(senha, row["senha_hash"]):
        return None

    return {
        "id": row["id"],
        "email": row["email"],
        "role": row["role"],
        "nome": row["nome"],
    }


def obter_usuario_atual(token: str = Depends(oauth2_scheme)) -> dict:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = payload.get("sub")
        role = payload.get("role")
        if not usuario_id or not role:
            raise credenciais_invalidas
        return {"usuario_id": usuario_id, "role": role, "email": payload.get("email")}
    except jwt.PyJWTError:
        raise credenciais_invalidas


def exigir_role(role_requerida: str):
    def _dependencia(usuario: dict = Depends(obter_usuario_atual)) -> dict:
        if usuario["role"] != role_requerida:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito a usuários com perfil '{role_requerida}'",
            )
        return usuario

    return _dependencia


def exigir_coletor(usuario: dict = Depends(obter_usuario_atual)) -> dict:
    if usuario["role"] != "coletor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a coletores",
        )
    return usuario


def exigir_autenticado(usuario: dict = Depends(obter_usuario_atual)) -> dict:
    return usuario
