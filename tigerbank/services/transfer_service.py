from __future__ import annotations
from decimal import Decimal
from tigerbank.extensions import db
from tigerbank.models import Account, Transaction
from .account_service import _as_decimal, InvalidAmount, InsufficientFunds

def transfer(from_account_id: int, to_account_id: int, amount: float, description: str = "Transferência"):
    amt = _as_decimal(amount)
    if amt <= 0:
        raise InvalidAmount("valor invalido")
    if from_account_id == to_account_id:
        raise ValueError("mesma conta")
    # se já houver transação ativa, usa SAVEPOINT para evitar "A transaction is already begun"
    with db.session.begin_nested():
        orig = db.session.get(Account, from_account_id)
        dest = db.session.get(Account, to_account_id)
        if _as_decimal(orig.balance) < amt:
            raise InsufficientFunds("saldo insuficiente")
        orig.balance = _as_decimal(orig.balance) - amt
        dest.balance = _as_decimal(dest.balance) + amt
        db.session.add(Transaction(
            account_id=orig.id,
            kind="Transferência Enviada",
            amount=-amt,
            description=f"{description} - Para: {dest.user.name}",
            balance_after=orig.balance
        ))
        db.session.add(Transaction(
            account_id=dest.id,
            kind="Transferência Recebida",
            amount=amt,
            description=f"{description} - De: {orig.user.name}",
            balance_after=dest.balance
        ))
