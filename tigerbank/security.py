from __future__ import annotations
from passlib.context import CryptContext

# Passlib configurado para bcrypt (seguro e recomendado)
_pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# Prefixos de hashes antigos (compatibilidade com contas já existentes)
_WERKZEUG_PREFIXES = ("pbkdf2:sha256:", "scrypt:")

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """
    Sempre gera hashes novos usando bcrypt (via passlib),
    garantindo segurança moderna.
    """
    return _pwd.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifica senha com suporte a dois formatos:
    - bcrypt (passlib) → padrão novo
    - pbkdf2/scrypt (werkzeug) → legado
    """
    try:
        # hash legado (Werkzeug)
        if stored_hash.startswith(_WERKZEUG_PREFIXES):
            return check_password_hash(stored_hash, password)

        # hash moderno (bcrypt/passlib)
        return _pwd.verify(password, stored_hash)

    except Exception:
        return False
