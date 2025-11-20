from __future__ import annotations
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from tigerbank.models import Transaction
from datetime import datetime

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.get("/")
@login_required
def index():
    # garante que o usuário tem conta vinculada
    acc = getattr(current_user, "account", None)
    if acc is None:
        return abort(403)

    # --- Cálculo simples de gastos do mês atual ---
    now = datetime.utcnow()
    mes_atual = now.month
    ano_atual = now.year

    gastos_mes = (
        Transaction.query
        .filter_by(account_id=acc.id)
        .filter(Transaction.value < 0)  # gastos → valores negativos
        .filter(Transaction.date.month == mes_atual)
        .filter(Transaction.date.year == ano_atual)
        .with_entities(Transaction.value)
        .all()
    )

    total_gastos_mes = sum(abs(t.value) for t in gastos_mes)

    return render_template(
        "dashboard.html",
        account=acc,
        total_gastos_mes=total_gastos_mes,
    )
