from passlib.hash import bcrypt as _bcrypt

_MAX = 72

def _normalize(p: str) -> bytes:
    return p.encode("utf-8")

def _truncate(b: bytes) -> bytes:
    return b[:_MAX]

def hash_password(password: str) -> str:
    return _bcrypt.hash(_truncate(_normalize(password)))

def verify_password(password: str, hashed: str) -> bool:
    return _bcrypt.verify(_truncate(_normalize(password)), hashed)
