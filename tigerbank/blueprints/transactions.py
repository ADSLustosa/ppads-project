# tigerbank/blueprints/transactions.py
from __future__ import annotations
import secrets
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from tigerbank.extensions import db
from tigerbank.models import User, Account, Transaction, Investment
from tigerbank.security import hash_password

bp = Blueprint("tx", __name__, url_prefix="/tx")


# ============================================================
# UTILITÁRIOS FINANCEIROS / CONVERSÃO
# ============================================================

def _q(v) -> Decimal:
    """Converte para Decimal com 2 casas."""
    return Decimal(str(v)).quantize(Decimal("0.01"))


def _to_float(s: str) -> float:
    """Converte valores formatados como R$ para float."""
    if not s:
        return 0.0
    s = s.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(Decimal(s))
    except Exception:
        return 0.0


def _rollback():
    try:
        db.session.rollback()
    except Exception:
        pass


# ============================================================
# CONTAS E USUÁRIOS
# ============================================================

def _ensure_account() -> Account:
    """Garante que o usuário autenticado tenha uma conta."""
    if getattr(current_user, "is_authenticated", False) and getattr(current_user, "account", None):
        return current_user.account

    # Conta automática de teste
    u = User.query.filter_by(email="teste@tigerbank.com").first()
    if not u:
        u = User(
            cpf="1"*11,
            name="Conta Teste",
            email="teste@tigerbank.com",
            password_hash=hash_password("Teste123@")
        )
        db.session.add(u)
        db.session.flush()
        db.session.add(Account(user_id=u.id, type="Corrente", balance=_q(0)))
        db.session.commit()
    return u.account  # type: ignore


def _ensure_recipient(orig: Account) -> Account:
    """Garante que sempre exista um destinatário válido."""
    other = Account.query.filter(Account.id != orig.id).first()
    if other:
        return other

    u = User(
        cpf="9"*11,
        name="Destinatário Automático",
        email=f"auto-{secrets.token_hex(3)}@local.test",
        password_hash=hash_password("Teste123@"),
    )
    db.session.add(u)
    db.session.flush()

    acc = Account(user_id=u.id, type="Corrente", balance=_q(0))
    db.session.add(acc)
    db.session.commit()
    return acc


# ============================================================
# CENTRALIZAÇÃO DE OPERAÇÕES FINANCEIRAS (PADRÃO BANCÁRIO)
# ============================================================

def _debit(acc: Account, valor: Decimal, desc: str, kind: str):
    """Debita valor da conta com proteção 100% anti-saldo-negativo."""
    valor = _q(valor)

    if valor <= 0:
        raise ValueError("Valor inválido.")

    if _q(acc.balance) - valor < 0:
        raise ValueError("Saldo insuficiente.")

    acc.balance = _q(acc.balance) - valor
    _post_tx(acc.id, kind, -valor, desc, acc.balance)


def _credit(acc: Account, valor: Decimal, desc: str, kind: str):
    """Credita valor na conta com validação."""
    valor = _q(valor)

    if valor <= 0:
        raise ValueError("Valor inválido.")

    acc.balance = _q(acc.balance) + valor
    _post_tx(acc.id, kind, valor, desc, acc.balance)


def _post_tx(acc_id: int, kind: str, amount: Decimal, desc: str, new_balance: Decimal):
    """Registra transação no extrato."""
    db.session.add(Transaction(
        account_id=acc_id,
        kind=kind,
        amount=amount,
        description=desc,
        balance_after=new_balance
    ))


# ============================================================
# PRODUTOS DE INVESTIMENTO (SIMULAÇÃO)
# ============================================================

def _investment_products() -> dict:
    return {
        "cdb_pos": {"name": "CDB Pós-fixado", "rate": 0.012},
        "tesouro": {"name": "Tesouro Selic", "rate": 0.010},
        "fii_mxrf": {"name": "MXRF11", "rate": 0.015},
        "lci": {"name": "LCI Habitação", "rate": 0.009},
    }


# ============================================================
# ROTAS FINANCEIRAS
# ============================================================

# ---------------------- DEPÓSITO ----------------------------
@bp.route("/deposito", methods=["GET", "POST"])
def deposito():
    if request.method == "POST":
        acc = _ensure_account()
        valor = _q(_to_float(request.form.get("valor", "")))
        desc = request.form.get("descricao", "Depósito")

        try:
            _rollback()
            _credit(acc, valor, desc, "Depósito")
            db.session.commit()
            flash("Depósito realizado com sucesso.", "success")
        except ValueError as e:
            flash(str(e), "error")

        return redirect(url_for("dashboard.index"))

    return render_template("deposito.html")


# ---------------------- SAQUE -------------------------------
@bp.route("/saque", methods=["GET", "POST"])
def saque():
    if request.method == "POST":
        acc = _ensure_account()
        valor = _q(_to_float(request.form.get("valor", "")))
        desc = request.form.get("descricao", "Saque")

        try:
            _rollback()
            _debit(acc, valor, desc, "Saque")
            db.session.commit()
            flash("Saque realizado com sucesso.", "success")
        except ValueError as e:
            flash(str(e), "error")

        return redirect(url_for("dashboard.index"))

    return render_template("saque.html")


# ---------------------- TRANSFERÊNCIA ------------------------
@bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    if request.method == "POST":
        origem = _ensure_account()
        dest = _ensure_recipient(origem)
        valor = _q(_to_float(request.form.get("valor", "")))

        try:
            _rollback()
            _debit(origem, valor, "Transferência", "Transferência Enviada")
            _credit(dest, valor, "Transferência", "Transferência Recebida")
            db.session.commit()
            flash("Transferência concluída.", "success")
        except ValueError as e:
            flash(str(e), "error")

        return redirect(url_for("dashboard.index"))

    return render_template("transferencia.html")


# ---------------------- PIX ---------------------------------
@bp.route("/pix", methods=["GET", "POST"])
def pix():
    if request.method == "POST":
        origem = _ensure_account()
        dest = _ensure_recipient(origem)
        valor = _q(_to_float(request.form.get("valor", "")))

        try:
            _rollback()
            _debit(origem, valor, "PIX", "PIX Enviado")
            _credit(dest, valor, "PIX", "PIX Recebido")
            db.session.commit()
            flash("PIX enviado com sucesso.", "success")
        except ValueError as e:
            flash(str(e), "error")

        return redirect(url_for("dashboard.index"))

    return render_template("pix.html")


# ---------------------- EXTRATO ------------------------------
@bp.get("/extrato")
def extrato():
    acc = _ensure_account()
    txs = (
        Transaction.query
        .filter_by(account_id=acc.id)
        .order_by(Transaction.created_at.desc())
        .limit(200)
        .all()
    )
    return render_template("extrato.html", txs=txs)


# ---------------------- INVESTIMENTOS ------------------------
@bp.route("/investimentos", methods=["GET", "POST"])
def investimentos():
    acc = _ensure_account()
    produtos = _investment_products()

    # 🔥 Agora puxa investimentos reais
    investimentos = Investment.query.filter_by(account_id=acc.id).all()

    if request.method == "POST":
        valor = _q(_to_float(request.form.get("valor", "0")))
        produto_key = request.form.get("produto")
        meses = int(request.form.get("meses", "0"))

        produto_escolhido = produtos.get(produto_key)
        if not produto_escolhido:
            flash("Produto inválido!", "error")
            return redirect(url_for("tx.investimentos"))

        # 🔥 Evita saldo negativo
        if acc.balance < valor:
            flash("Saldo insuficiente!", "error")
            return redirect(url_for("tx.investimentos"))

        _rollback()

        # Atualiza saldo
        acc.balance = _q(acc.balance) - valor

        # Registra transação
        _post_tx(
            acc.id,
            "Investimento",
            -valor,
            f"{produto_escolhido['name']} ({meses}m)",
            acc.balance
        )

        # 🔥 Salva o investimento usando os CAMPOS EXATOS do seu model
        novo = Investment(
            account_id=acc.id,
            product=produto_escolhido["name"],
            monthly_rate=float(produto_escolhido["rate"]),
            principal=float(valor),
            months=meses,
            active=True
        )

        db.session.add(novo)
        db.session.commit()

        flash("Investimento realizado com sucesso!", "success")
        return redirect(url_for("tx.investimentos"))

    return render_template(
        "investimentos.html",
        produtos=produtos,
        investimentos=investimentos
    )



# ---------------------- RESGATE ------------------------------
@bp.post("/investimentos/<int:inv_id>/resgatar")
def resgatar(inv_id: int):
    acc = _ensure_account()
    inv = Investment.query.filter_by(id=inv_id, account_id=acc.id).first()

    if not inv:
        flash("Investimento não encontrado.", "error")
        return redirect(url_for("tx.investimentos"))

    if not inv.active:
        flash("Este investimento já foi resgatado.", "error")
        return redirect(url_for("tx.investimentos"))

    _rollback()

    # 🔥 Calcula resgate simples (sem juros por enquanto)
    valor = _q(inv.principal)

    acc.balance = _q(acc.balance) + valor
    inv.active = False

    _post_tx(
        acc.id,
        "Resgate",
        valor,
        f"Resgate de {inv.product}",
        acc.balance
    )

    db.session.commit()
    flash("Resgate efetuado com sucesso!", "success")
    return redirect(url_for("tx.investimentos"))

# ---------------------- EMPRÉSTIMO ---------------------------
@bp.route("/emprestimo", methods=["GET", "POST"])
def emprestimo():
    if request.method == "POST":
        acc = _ensure_account()
        valor = _q(_to_float(request.form.get("valor", "")))
        parcelas = request.form.get("meses", "0")

        try:
            _rollback()
            _credit(acc, valor, f"Empréstimo aprovado ({parcelas}x)", "Empréstimo")
            db.session.commit()
            flash("Empréstimo aprovado com sucesso.", "success")
        except ValueError as e:
            flash(str(e), "error")

        return redirect(url_for("dashboard.index"))

    return render_template("emprestimo.html")
