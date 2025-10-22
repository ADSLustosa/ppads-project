# tigerbank/security.py
from passlib.context import CryptContext

# Suporta hashes antigos "bcrypt" e usa "bcrypt_sha256" para novos (sem limite prático de 72B)
_pwd = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return _pwd.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return _pwd.verify(password, hashed)
