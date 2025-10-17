
from __future__ import annotations
import re

CPF_RE = re.compile(r"^\d{11}$")

def is_valid_cpf(cpf: str) -> bool:
    if not CPF_RE.match(cpf or ""):
        return False
    # validação simples de dígitos (placeholder); regra completa pode ser aplicada depois
    return True

def strong_password(p: str) -> bool:
    if len(p) < 8: return False
    if not re.search(r"[A-Z]", p): return False
    if not re.search(r"[a-z]", p): return False
    if not re.search(r"\d", p): return False
    return True
