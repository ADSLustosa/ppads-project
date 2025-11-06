from __future__ import annotations
from decimal import Decimal
from tigerbank.extensions import db
from tigerbank.models import Account, Transaction, Loan
from .account_service import _as_decimal

def _reset_session() -> None:
    try:
        db.session.rollback()
    except Exception:
        pass

def hire_loan(account_id: int, principal: float, months: int,
                monthly_rate: float=0.025) -> Loan:
    p = _as_decimal(principal)
    if p < Decimal("500") or p > Decimal("50000"):
        raise ValueError("fora da faixa")
    if months not in (6, 12, 18, 24):
        raise ValueError("parcelas invalidas")
    _reset_session()
    with db.session.begin():
        acc = db.session.get(Account, account_id)
        total = p * Decimal(str((1 + monthly_rate) ** months))
        installment = total / months
        loan = Loan(account_id=acc.id, principal=p, months=months,
                    monthly_rate=monthly_rate, installment_amount=installment,
                    remaining_installments=months)
        db.session.add(loan)
        acc.balance = _as_decimal(acc.balance) + p
        tx = Transaction(account_id=acc.id, kind="Empréstimo Aprovado", amount=p,
                            description=f"Empréstimo - {months}x de {installment.quantize(Decimal('0.01'))}",
                            balance_after=acc.balance)
        db.session.add(tx)
        return loan
