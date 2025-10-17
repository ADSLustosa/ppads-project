
from __future__ import annotations
from decimal import Decimal
from tigerbank.extensions import db
from tigerbank.models import Account, Transaction, Investment
from .account_service import _as_decimal, InsufficientFunds

PRODUCTS = {
    "poupanca": {"name": "Poupança", "rate": 0.005},
    "cdb": {"name": "CDB", "rate": 0.01},
    "acoes": {"name": "Ações", "rate": 0.02},  # simples
}

def invest(account_id: int, product_key: str, principal: float, months: int) -> Investment:
    if product_key not in PRODUCTS:
        raise ValueError("produto invalido")
    p = _as_decimal(principal)
    if p < Decimal("100"):
        raise ValueError("minimo 100")
    with db.session.begin():
        acc = db.session.get(Account, account_id)
        if _as_decimal(acc.balance) < p:
            raise InsufficientFunds("saldo insuficiente")
        acc.balance = _as_decimal(acc.balance) - p
        prod = PRODUCTS[product_key]
        inv = Investment(account_id=acc.id, product=prod["name"], monthly_rate=prod["rate"], principal=p, months=months, active=True)
        db.session.add(inv)
        db.session.add(Transaction(account_id=acc.id, kind="Investimento", amount=-p, description=f"Investimento em {prod['name']} - {months} meses", balance_after=acc.balance))
        return inv

def redeem(account_id: int, investment_id: int):
    with db.session.begin():
        inv = db.session.get(Investment, investment_id)
        if inv.account_id != account_id or not inv.active:
            raise ValueError("invalido")
        total = inv.principal * Decimal(str((1+inv.monthly_rate) ** inv.months))
        acc = inv.account
        acc.balance = _as_decimal(acc.balance) + total
        inv.active = False
        db.session.add(Transaction(account_id=acc.id, kind="Resgate de Investimento", amount=total, description=f"Resgate {inv.product}", balance_after=acc.balance))
        return total
