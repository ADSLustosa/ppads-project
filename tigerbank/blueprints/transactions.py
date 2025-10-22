
from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from tigerbank.models import User, Transaction, Account
from tigerbank.services import account_service, transfer_service
from tigerbank.services.investment_service import invest, redeem, PRODUCTS
from tigerbank.services.loan_service import hire_loan

bp = Blueprint("tx", __name__, url_prefix="/tx")

@bp.route("/deposito", methods=["GET","POST"])
@login_required
def deposito():
    if request.method == "POST":
        valor = float(request.form.get("valor", "0"))
        desc = request.form.get("descricao","Depósito")
        try:
            account_service.deposit(current_user.account.id, valor, desc)
            flash("Depósito realizado", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("deposito.html")

@bp.route("/saque", methods=["GET","POST"])
@login_required
def saque():
    if request.method == "POST":
        valor = float(request.form.get("valor", "0"))
        desc = request.form.get("descricao","Saque")
        try:
            account_service.withdraw(current_user.account.id, valor, desc)
            flash("Saque realizado", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("saque.html")

@bp.route("/transferencia", methods=["GET","POST"])
@login_required
def transferencia():
    if request.method == "POST":
        cpf_dest = request.form.get("cpf","").strip()
        valor = float(request.form.get("valor", "0"))
        dest_user = User.query.filter_by(cpf=cpf_dest).first()
        if not dest_user:
            flash("Destinatário não encontrado", "error")
        elif dest_user.id == current_user.id:
            flash("Não transfira para si", "error")
        else:
            try:
                transfer_service.transfer(current_user.account.id, dest_user.account.id, valor, "Transferência")
                flash("Transferência concluída", "success")
                return redirect(url_for("dashboard.index"))
            except Exception as e:
                flash(str(e), "error")
    return render_template("transferencia.html")

@bp.route("/pix", methods=["GET","POST"])
@login_required
def pix():
    if request.method == "POST":
        chave = request.form.get("chave","").strip().lower()
        valor = float(request.form.get("valor", "0"))
        # nesta versão simples, PIX por e-mail
        dest = User.query.filter_by(email=chave).first()
        if not dest or dest.id == current_user.id:
            flash("Chave PIX inválida", "error")
        else:
            from tigerbank.services.transfer_service import transfer
            try:
                transfer(current_user.account.id, dest.account.id, valor, "PIX")
                flash("PIX enviado", "success")
                return redirect(url_for("dashboard.index"))
            except Exception as e:
                flash(str(e), "error")
    return render_template("pix.html")

@bp.get("/extrato")
@login_required
def extrato():
    txs = (Transaction.query
           .filter_by(account_id=current_user.account.id)
           .order_by(Transaction.created_at.desc())
           .limit(200).all())
    return render_template("extrato.html", txs=txs)

@bp.route("/investimentos", methods=["GET","POST"])
@login_required
def investimentos():
    if request.method == "POST":
        produto = request.form.get("produto")
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

@bp.post("/investimentos/<int:inv_id>/resgatar")
@login_required
def resgatar(inv_id: int):
    try:
        from tigerbank.services.investment_service import redeem
        redeem(current_user.account.id, inv_id)
        flash("Resgate efetuado", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("tx.investimentos"))

@bp.route("/emprestimo", methods=["GET","POST"])
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
