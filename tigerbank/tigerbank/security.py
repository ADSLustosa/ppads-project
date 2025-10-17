
from __future__ import annotations
from passlib.hash import bcrypt
from hashlib import sha256

def _normalize(p: str) -> str:
    b = p.encode("utf-8")
    if len(b) > 72:
        return sha256(b).hexdigest()
    return p

def hash_password(password: str) -> str:
    return bcrypt.hash(_normalize(password))

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(_normalize(password), hashed)