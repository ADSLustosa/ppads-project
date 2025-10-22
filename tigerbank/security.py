from __future__ import annotations
from hashlib import sha256
from passlib.context import CryptContext

# aceita hashes antigos (bcrypt) e novos (pbkdf2_sha256)
_pwd = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto"
)

def _normalize(password: str) -> str:
    """Trunca ou reduz senhas longas para compatibilidade."""
    data = password.encode("utf-8")
    return sha256(data).hexdigest() if len(data) > 72 else password

def hash_password(password: str) -> str:
    """Gera hash seguro com pbkdf2_sha256."""
    return _pwd.hash(_normalize(password))

def verify_password(password: str, hashed: str) -> bool:
    """Verifica senhas em bcrypt ou pbkdf2_sha256."""
    normalized = _normalize(password)
    return _pwd.verify(normalized, hashed)
