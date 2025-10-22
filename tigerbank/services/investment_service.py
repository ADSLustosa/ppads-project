from __future__ import annotations
from decimal import Decimal, ROUND_DOWN
from datetime import datetime
from sqlalchemy import select
from tigerbank.extensions import db
from tigerbank.models import Account, Investment, Transaction

# Produtos disponíveis e suas taxas mensais
PRODUCTS: dict[str, Decimal] = {
    "CDB": Decimal("0.012"),      # 1.2% a.m.
    "LCI": Decimal("0.010"),      # 1.0% a.m.
    "LCA": Decimal("0.011"),      # 1.1% a.m.
    "POUPANCA": Decimal("0.005"), # 0.5% a.m.
}

class InsufficientFunds(Exception): ...
class InvalidAmount(Exception): ...

def _as_decimal(value: float | Decimal) -> Decimal:
    """Converte valores para Decimal com duas casas decimais."""
    d = Decimal(str(value)) if not isinstance(value, Decimal) else value
    return d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def invest(account_id: int, product: str, amount: float, months: int) -> Investment:
    """Realiza um investimento retirando saldo da conta."""
    if product not in PRODUCTS:
        raise ValueError("produto de investimento inválido")

    if months <= 0:
        raise ValueError("prazo inválido")

    amt = _as_decimal(amount)
    if amt <= 0:
        raise InvalidAmount("valor inválido para investimento")

    with db.session.begin_nested():
        acc = db.session.get(Account, account_id)
        if not acc:
            raise ValueError("conta não encontrada")

        if _as_decimal(acc.balance) < amt:
            raise InsufficientFunds("saldo insuficiente para investir")

        # Debita o valor da conta
        acc.balance = _as_decimal(acc.balance) - amt

        # Cria o investimento (usa campos definidos em models.py)
        inv = Investment(
            account_id=acc.id,
            product=product,
            monthly_rate=float(PRODUCTS[product]),
            principal=amt,
            months=months,
            started_at=datetime.utcnow(),
            active=True,
        )
        db.session.add(inv)

        # Registra a transação no extrato
        tx = Transaction(
            account_id=acc.id,
            kind="Investimento",
            amount=-amt,
            description=f"Investimento em {product}",
            balance_after=acc.balance,
        )
        db.session.add(tx)

        return inv

def redeem(account_id: int, investment_id: int) -> Transaction:
    """Resgata um investimento e credita o valor na conta."""
    with db.session.begin_nested():
        inv = db.session.get(Investment, investment_id)
        if not inv:
            raise ValueError("investimento não encontrado")

        if inv.account_id != account_id:
            raise ValueError("investimento não pertence à conta informada")

        if not inv.active:
            raise ValueError("investimento já resgatado")

        acc = db.session.get(Account, inv.account_id)
        if not acc:
            raise ValueError("conta não encontrada")

        # Calcula rendimento simples (exemplo). Ajuste para composto se quiser.
        principal = _as_decimal(inv.principal)
        rate = _as_decimal(inv.monthly_rate)
        months = int(inv.months) if inv.months else 0

        total = _as_decimal(principal * (Decimal("1") + rate * Decimal(months)))

        # Marca investimento como encerrado
        inv.active = False
        try:
            inv.ended_at = datetime.utcnow()
        except Exception:
            pass

        # Credita o valor na conta
        acc.balance = _as_decimal(acc.balance) + total

        # Registra transação de crédito
        tx = Transaction(
            account_id=acc.id,
            kind="Resgate",
            amount=total,
            description=f"Resgate de investimento {inv.product}",
            balance_after=acc.balance,
        )
        db.session.add(tx)

        return tx

def list_investments(account_id: int) -> list[Investment]:
    """Lista todos os investimentos de uma conta."""
    stmt = select(Investment).where(Investment.account_id == account_id)
    return db.session.scalars(stmt).all()