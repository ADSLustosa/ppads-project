from __future__ import annotations
from datetime import date, datetime, time
from decimal import Decimal
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from tigerbank.models import User, Transaction
from tigerbank.services import account_service, transfer_service
from tigerbank.services.investment_service import invest, redeem, PRODUCTS
from tigerbank.services.loan_service import hire_loan
from tigerbank.services.transfer_service import transfer as do_transfer

bp = Blueprint("tx", __name__, url_prefix="/tx")

# -------- Depósito
@bp.route("/deposito", methods=["GET", "POST"], endpoint="deposito")
@login_required
def deposito():
    if request.method == "POST":
        valor = float(request.form.get("valor", "0"))
        desc = request.form.get("descricao", "Depósito")
        try:
            account_service.deposit(current_user.account.id, valor, desc)
            flash("Depósito realizado", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("deposito.html")

# -------- Saque
@bp.route("/saque", methods=["GET", "POST"], endpoint="saque")
@login_required
def saque():
    if request.method == "POST":
        valor = float(request.form.get("valor", "0"))
        desc = request.form.get("descricao", "Saque")
        try:
            account_service.withdraw(current_user.account.id, valor, desc)
            flash("Saque realizado", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("saque.html")

# -------- Transferência
@bp.route("/transferencia", methods=["GET", "POST"], endpoint="transferencia")
@login_required
def transferencia():
    if request.method == "POST":
        cpf_dest = request.form.get("cpf", "").strip()
        valor = float(request.form.get("valor", "0"))
        dest_user = User.query.filter_by(cpf=cpf_dest).first()
        if not dest_user:
            flash("Destinatário não encontrado", "error")
        elif dest_user.id == current_user.id:
            flash("Não transfira para si", "error")
        else:
            try:
                transfer_service.transfer(
                    current_user.account.id, dest_user.account.id, valor, "Transferência"
                )
                flash("Transferência concluída", "success")
                return redirect(url_for("dashboard.index"))
            except Exception as e:
                flash(str(e), "error")
    return render_template("transferencia.html")

# -------- PIX
def _only_digits(s: str) -> str:
    return re.sub(r"\D+", "", s or "")

def _detect_key_type(raw: str) -> str:
    s = (raw or "").strip().lower()
    if "@" in s: return "email"
    d = _only_digits(s)
    if len(d) in (11, 14): return "cpf_cnpj"
    if len(d) in (10, 11): return "celular"
    return "aleatoria"

def _find_user_by_key(raw: str) -> User | None:
    k = _detect_key_type(raw)
    if k == "email":
        return User.query.filter_by(email=raw.strip().lower()).first()
    if k == "cpf_cnpj":
        doc = _only_digits(raw)
        u = User.query.filter_by(cpf=doc).first()
        if u: return u
        if hasattr(User, "cnpj"):
            return User.query.filter_by(cnpj=doc).first()
        return None
    if k == "celular" and hasattr(User, "phone"):
        return User.query.filter_by(phone=_only_digits(raw)).first()
    return None

@bp.route("/pix", methods=["GET", "POST"], endpoint="pix")
@login_required
def pix():
    if request.method == "GET":
        return render_template("pix.html", today=date.today().isoformat())

    chave = (request.form.get("chave") or "").strip()
    valor_str = (request.form.get("valor") or "0").replace(",", ".")
    agendado = request.form.get("agendado") == "1"
    data_agendada = request.form.get("data_agendada") or ""
    hora_agendada = request.form.get("hora_agendada") or "09:00"

    try:
        valor = Decimal(valor_str)
    except Exception:
        flash("Valor inválido.", "error")
        return redirect(url_for("tx.pix"))
    if valor <= 0:
        flash("Valor deve ser maior que zero.", "error")
        return redirect(url_for("tx.pix"))

    if agendado:
        try:
            dt = date.fromisoformat(data_agendada)
            hh, mm = (hora_agendada or "09:00").split(":")
            tm = time(int(hh), int(mm))
            when = datetime.combine(dt, tm)
        except Exception:
            flash("Data/horário do agendamento inválidos.", "error")
            return redirect(url_for("tx.pix"))
    if when < datetime.now():
        flash("Agendamento não pode ser no passado.", "error")
        return redirect(url_for("tx.pix"))
    flash(f"Agendamento registrado para {when.strftime('%d/%m/%Y %H:%M')}. Execução automática não implementada.", "success")
    return redirect(url_for("dashboard.index"))

    dest = _find_user_by_key(chave)
    if not dest:
        flash("Chave PIX não encontrada ou não suportada.", "error")
        return redirect(url_for("tx.pix"))
    if dest.id == current_user.id:
        flash("Não é permitido enviar PIX para si próprio.", "error")
        return redirect(url_for("tx.pix"))

    try:
        do_transfer(current_user.account.id, dest.account.id, float(valor), "PIX")
        flash("PIX enviado.", "success")
        return redirect(url_for("dashboard.index"))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("tx.pix"))

# -------- Extrato e Investimentos (inalterados)
@bp.get("/extrato", endpoint="extrato")
@login_required
def extrato():
    txs = (Transaction.query
        .filter_by(account_id=current_user.account.id)
        .order_by(Transaction.created_at.desc())
        .limit(200).all())
    return render_template("extrato.html", txs=txs)

@bp.route("/investimentos", methods=["GET","POST"], endpoint="investimentos")
@login_required
def investimentos():
    if request.method == "POST":
        produto = request.form.get("produto", "")
        valor = float(request.form.get("valor","0"))
        meses = int(request.form.get("meses","0"))
        try:
            invest(current_user.account.id, produto, valor, meses)
            flash("Investimento realizado", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(str(e), "error")
    ativos = current_user.account.investments
    return render_template("investimentos.html", produtos=PRODUCTS, investimentos=ativos)

@bp.post("/investimentos/<int:inv_id>/resgatar", endpoint="resgatar")
@login_required
def resgatar(inv_id: int):
    try:
        redeem(current_user.account.id, inv_id)
        flash("Resgate efetuado", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("tx.investimentos"))

@bp.route("/emprestimo", methods=["GET","POST"], endpoint="emprestimo")
@login_required
def emprestimo():
    if request.method == "POST":
        valor = float(request.form.get("valor","0"))
        meses = int(request.form.get("meses","0"))
        try:
            hire_loan(current_user.account.id, valor, meses)
            flash("Empréstimo aprovado", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("emprestimo.html")
