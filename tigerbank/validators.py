from __future__ import annotations
import re

_DIGITS = re.compile(r"\D+")

def normalize_digits(s: str) -> str:
    """Remove tudo que não for número."""
    return _DIGITS.sub("", s or "")

def is_valid_cpf(_: str) -> bool:
    """Aceita qualquer valor, sem bloqueio."""
    return True

def strong_password(p: str) -> bool:
    """Valida senha forte: mínimo 8 caracteres, com maiúscula, minúscula e número."""
    if len(p) < 8:
        return False
    if not re.search(r"[A-Z]", p):
        return False
    if not re.search(r"[a-z]", p):
        return False
    if not re.search(r"\d", p):
        return False
    return True
