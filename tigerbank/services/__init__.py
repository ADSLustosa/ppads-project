# Marca o pacote de serviços e facilita importações
from __future__ import annotations

from . import account_service, transfer_service, investment_service, loan_service

__all__ = [
    "account_service",
    "transfer_service",
    "investment_service",
    "loan_service",
]
