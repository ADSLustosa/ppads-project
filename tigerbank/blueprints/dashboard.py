from __future__ import annotations
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from tigerbank.models import Account, Transaction

# NOME CORRETO DO BLUEPRINT: dashboard_bp
dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
    template_folder="../templates",
)

@dashboard_bp.get("/")
@login_required
def index():
    acc = current_user.account
    gastos_mes = 0
    # cálculo simples de gastos do mês

    return render_template("dashboard.html", account=acc)
