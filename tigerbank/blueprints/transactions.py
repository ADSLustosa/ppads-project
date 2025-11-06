# tigerbank/blueprints/transactions.py
from __future__ import annotations
import secrets
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from tigerbank.extensions import db
from tigerbank.models import User, Account, Transaction
from tigerbank.security import hash_password

bp = Blueprint("tx", __name__, url_prefix="/tx")

# ---------- utils ----------
def _q(v) -> Decimal:
    return Decimal(str(v)).quantize(Decimal("0.01"))

def _to_float(s: str) -> float:
    s = (s or "0").replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(Decimal(s))
    except Exception:
        return 0.0

def _rollback():
    try:
        db.session.rollback()
    except Exception:
        pass

def _ensure_account() -> Account:
    if getattr(current_user, "is_authenticated", False) and getattr(current_user, "account", None):
        return current_user.account
    u = User.query.filter_by(email="teste@tigerbank.com").first()
    if not u:
        u = User(
            cpf="1"*11, name="Conta Teste", email="teste@tigerbank.com",
            password_hash=hash_password("Teste123@")
        )
        db.session.add(u); db.session.flush()
        db.session.add(Account(user_id=u.id, type="Corrente", balance=_q(0)))
        db.session.commit()
    return u.account  # type: ignore[attr-defined]

def _ensure_recipient(orig: Account) -> Account:
    other = Account.query.filter(Account.id != orig.id).first()
    if other:
        return other
    u = User(
        cpf="9"*11,
        name="Destinatário Automático",
        email=f"auto-{secrets.token_hex(3)}@example.test",
        password_hash=hash_password("Teste123@"),
    )
    db.session.add(u); db.session.flush()
    acc = Account(user_id=u.id, type="Corrente", balance=_q(0))
    db.session.add(acc); db.session.commit()
    return acc

def _post_tx(acc_id: int, kind: str, amount: Decimal, desc: str, new_balance: Decimal):
    db.session.add(Transaction(
        account_id=acc_id, kind=kind, amount=amount, description=desc, balance_after=new_balance
    ))
# ---------------------------

@bp.route("/deposito", methods=["GET", "POST"])
def deposito():
    if request.method == "POST":
        valor = _q(_to_float(request.form.get("valor", "0")))
        desc = request.form.get("descricao", "Depósito")
        acc = _ensure_account()
        _rollback()
        acc.balance = _q(acc.balance) + valor
        _post_tx(acc.id, "Depósito", valor, desc, acc.balance)
        db.session.commit()
        flash("Depósito realizado.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("deposito.html")

@bp.route("/saque", methods=["GET", "POST"])
def saque():
    if request.method == "POST":
        valor = _q(_to_float(request.form.get("valor", "0")))
        desc = request.form.get("descricao", "Saque")
        acc = _ensure_account()
        _rollback()
        acc.balance = _q(acc.balance) - valor
        _post_tx(acc.id, "Saque", -valor, desc, acc.balance)
        db.session.commit()
        flash("Saque realizado.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("saque.html")

@bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    if request.method == "POST":
        origem = _ensure_account()
        valor = _q(_to_float(request.form.get("valor", "0")))
        # Ignora CPF informado. Garante destinatário válido.
        dest = _ensure_recipient(origem)
        _rollback()
        origem.balance = _q(origem.balance) - valor
        dest.balance = _q(dest.balance) + valor
        _post_tx(origem.id, "Transferência Enviada", -valor, "Transferência livre (teste)", origem.balance)
        _post_tx(dest.id, "Transferência Recebida", valor, "Transferência livre (teste)", dest.balance)
        db.session.commit()
        flash("Transferência concluída.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("transferencia.html")

@bp.route("/pix", methods=["GET", "POST"])
def pix():
    if request.method == "POST":
        origem = _ensure_account()
        valor = _q(_to_float(request.form.get("valor", "0")))
        # Ignora chave PIX. Garante destinatário válido.
        dest = _ensure_recipient(origem)
        _rollback()
        origem.balance = _q(origem.balance) - valor
        dest.balance = _q(dest.balance) + valor
        _post_tx(origem.id, "PIX Enviado", -valor, "PIX livre (teste)", origem.balance)
        _post_tx(dest.id, "PIX Recebido", valor, "PIX livre (teste)", dest.balance)
        db.session.commit()
        flash("PIX enviado.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("pix.html")

@bp.get("/extrato")
def extrato():
    acc = _ensure_account()
    txs = (Transaction.query
           .filter_by(account_id=acc.id)
           .order_by(Transaction.created_at.desc())
           .limit(200).all())
    return render_template("extrato.html", txs=txs)

@bp.route("/investimentos", methods=["GET", "POST"])
def investimentos():
    acc = _ensure_account()
    if request.method == "POST":
        valor = _q(_to_float(request.form.get("valor", "0")))
        produto = request.form.get("produto", "Simulação")
        meses = request.form.get("meses", "0")
        _rollback()
        acc.balance = _q(acc.balance) - valor
        _post_tx(acc.id, "Investimento", -valor, f"{produto} ({meses}m)", acc.balance)
        db.session.commit()
        flash("Investimento realizado.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("investimentos.html", produtos=[], investimentos=[])

@bp.post("/investimentos/<int:inv_id>/resgatar")
def resgatar(inv_id: int):
    acc = _ensure_account()
    _rollback()
    valor = _q(1)
    acc.balance = _q(acc.balance) + valor
    _post_tx(acc.id, "Resgate", valor, f"Resgate #{inv_id}", acc.balance)
    db.session.commit()
    flash("Resgate efetuado.", "success")
    return redirect(url_for("tx.investimentos"))

@bp.route("/emprestimo", methods=["GET", "POST"])
def emprestimo():
    if request.method == "POST":
        valor = _q(_to_float(request.form.get("valor", "0")))
        parcelas = request.form.get("meses", "0")
        acc = _ensure_account()
        _rollback()
        acc.balance = _q(acc.balance) + valor
        _post_tx(acc.id, "Empréstimo", valor, f"Empréstimo aprovado ({parcelas}x)", acc.balance)
        db.session.commit()
        flash("Empréstimo aprovado.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("emprestimo.html")
