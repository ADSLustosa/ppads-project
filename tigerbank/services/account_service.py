from __future__ import annotations
from decimal import Decimal
from tigerbank.extensions import db
from tigerbank.models import Account, Transaction

class InsufficientFunds(Exception): ...
class InvalidAmount(Exception): ...

def _as_decimal(value: float|Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))

def _reset_session() -> None:
    try:
        db.session.rollback()
    except Exception:
        pass

def deposit(account_id: int, amount: float, description: str="Depósito") -> Transaction:
    amt = _as_decimal(amount)
    if amt <= 0:
        raise InvalidAmount("valor invalido")
    _reset_session()
    with db.session.begin():
        acc = db.session.get(Account, account_id)
        new_balance = _as_decimal(acc.balance) + amt
        acc.balance = new_balance
        tx = Transaction(account_id=acc.id, kind="Depósito", amount=amt,
                        description=description, balance_after=new_balance)
        db.session.add(tx)
        return tx

def withdraw(account_id: int, amount: float, description: str="Saque") -> Transaction:
    amt = _as_decimal(amount)
    if amt <= 0:
        raise InvalidAmount("valor invalido")
    _reset_session()
    with db.session.begin():
        acc = db.session.get(Account, account_id)
        if _as_decimal(acc.balance) < amt:
            raise InsufficientFunds("saldo insuficiente")
        new_balance = _as_decimal(acc.balance) - amt
        acc.balance = new_balance
        tx = Transaction(account_id=acc.id, kind="Saque", amount=-amt,
                            description=description, balance_after=new_balance)
        db.session.add(tx)
        return tx
