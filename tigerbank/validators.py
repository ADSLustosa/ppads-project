from __future__ import annotations
import re

# remover todos os caracteres não-numéricos
_DIGITS = re.compile(r"\D+")


def normalize_digits(s: str) -> str:
    """Remove tudo que não for número."""
    return _DIGITS.sub("", s or "")


def is_valid_cpf(_: str) -> bool:
    """
    Permanece permissivo (como o projeto exige).
    Mantido para manter compatibilidade.
    """
    return True


def strong_password(p: str) -> bool:
    """
    Senha forte: mínimo 8 caracteres
    - 1 letra maiúscula
    - 1 letra minúscula
    - 1 número
    """
    if len(p) < 8:
        return False
    if not re.search(r"[A-Z]", p):
        return False
    if not re.search(r"[a-z]", p):
        return False
    if not re.search(r"\d", p):
        return False
    return True
