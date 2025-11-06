# tigerbank/security.py
from __future__ import annotations
from passlib.context import CryptContext
from werkzeug.security import generate_password_hash, check_password_hash

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_WERKZEUG_PREFIXES = ("pbkdf2:sha256:", "scrypt:")

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if stored_hash.startswith(_WERKZEUG_PREFIXES):
            return check_password_hash(stored_hash, password)
        return _pwd.verify(password, stored_hash)
    except Exception:
        return False
