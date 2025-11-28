# tigerbank/blueprints/transactions.py
from __future__ import annotations
import secrets
import re
from decimal import Decimal

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from tigerbank.extensions import db
from tigerbank.models import User, Account, Transaction
from tigerbank.security import hash_password

# === CORREÇÃO CRUCIAL AQUI ===
tx_bp = Blueprint(
    "tx",
    __name__,
    url_prefix="/tx",
    template_folder="../templates"
)

# ---------- catálogo de produtos de investimento ----------
INV_PRODUTOS: dict[str, dict] = {
    "cdb_100_cdi": {
        "codigo": "cdb_100_cdi",
        "nome": "CDB 100% do CDI",
        "descricao": "Renda fixa pós-fixada atrelada ao CDI.",
        "tipo": "Renda Fixa",
        "risco": "Baixo",
        "liquidez": "D+30",
        "taxa_mensal": Decimal("0.011"),
    },
    "tesouro_selic": {
        "codigo": "tesouro_selic",
        "nome": "Tesouro Selic",
        "descricao": "Título público federal pós-fixado.",
        "tipo": "Renda Fixa",
        "risco": "Muito Baixo",
        "liquidez": "D+1",
        "taxa_mensal": Decimal("0.009"),
    },
    "fii_mxrf11": {
        "codigo": "fii_mxrf11",
        "nome": "FII MXRF11",
        "descricao": "Fundo imobiliário de papel com foco em CRIs.",
        "tipo": "Fundos Imobiliários",
        "risco": "Médio",
        "liquidez": "D+2",
        "taxa_mensal": Decimal("0.012"),
    },
}

# ---------- Utils financeiros ----------
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
            cpf="1" * 11,
            name="Conta Teste",
            email="teste@tigerbank.com",
            password_hash=hash_password("Teste123@"),
        )
        db.session.add(u)
        db.session.flush()
        db.session.add(Account(user_id=u.id, type="Corrente", balance=_q(0)))
        db.session.commit()
    return u.account

def _ensure_recipient(orig: Account) -> Account:
    other = Account.query.filter(Account.id != orig.id).first()
    if other:
        return other
    u = User(
        cpf="9" * 11,
        name="Destinatário Automático",
        email=f"auto-{secrets.token_hex(3)}@example.test",
        password_hash=hash_password("Teste123@"),
    )
    db.session.add(u)
    db.session.flush()
    acc = Account(user_id=u.id, type="Corrente", balance=_q(0))
    db.session.add(acc)
    db.session.commit()
    return acc

def _post_tx(acc_id: int, kind: str, amount: Decimal, desc: str, new_balance: Decimal):
    db.session.add(
        Transaction(
            account_id=acc_id,
            kind=kind,
            amount=amount,
            description=desc,
            balance_after=new_balance,
        )
    )

def _simular_montante(valor: Decimal, taxa_mensal: Decimal, meses: int) -> tuple[Decimal, Decimal]:
    if meses <= 0 or taxa_mensal <= 0:
        return valor, _q(0)
    fator = (Decimal("1.0") + taxa_mensal) ** meses
    montante = _q(valor * fator)
    rendimento = _q(montante - valor)
    return montante, rendimento

def _parse_meses_descricao(desc: str) -> int:
    m = re.search(r"\((\d+)\s*m\)", desc)
    if not m:
        return 0
    try:
        return int(m.group(1))
    except ValueError:
        return 0

# --------------------------- ROTAS ---------------------------
@tx_bp.route("/deposito", methods=["GET", "POST"])
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

@tx_bp.route("/saque", methods=["GET", "POST"])
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

@tx_bp.route("/transferencia", methods=["GET", "POST"])
def transferencia():
    if request.method == "POST":
        origem = _ensure_account()
        valor = _q(_to_float(request.form.get("valor", "0")))
        dest = _ensure_recipient(origem)
        _rollback()
        origem.balance -= valor
        dest.balance += valor
        _post_tx(origem.id, "Transferência Enviada", -valor, "Transferência livre (teste)", origem.balance)
        _post_tx(dest.id, "Transferência Recebida", valor, "Transferência livre (teste)", dest.balance)
        db.session.commit()
        flash("Transferência concluída.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("transferencia.html")

@tx_bp.route("/pix", methods=["GET", "POST"])
def pix():
    if request.method == "POST":
        origem = _ensure_account()
        valor = _q(_to_float(request.form.get("valor", "0")))
        dest = _ensure_recipient(origem)
        _rollback()
        origem.balance -= valor
        dest.balance += valor
        _post_tx(origem.id, "PIX Enviado", -valor, "PIX livre (teste)", origem.balance)
        _post_tx(dest.id, "PIX Recebido", valor, "PIX livre (teste)", dest.balance)
        db.session.commit()
        flash("PIX enviado.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("pix.html")

@tx_bp.get("/extrato")
def extrato():
    acc = _ensure_account()
    txs = (
        Transaction.query.filter_by(account_id=acc.id)
        .order_by(Transaction.created_at.desc())
        .limit(200)
        .all()
    )
    return render_template("extrato.html", txs=txs)

@tx_bp.route("/investimentos", methods=["GET", "POST"])
def investimentos():
    acc = _ensure_account()
    produtos = INV_PRODUTOS

    if request.method == "POST":
        valor = _q(_to_float(request.form.get("valor", "0")))
        produto_codigo = request.form.get("produto", "")
        meses_str = request.form.get("meses", "0")

        try:
            meses = int(meses_str)
        except ValueError:
            meses = 0

        produto = INV_PRODUTOS.get(produto_codigo)
        if not produto:
            flash("Produto inválido.", "danger")
            return redirect(url_for("tx.investimentos"))

        montante, rendimento = _simular_montante(valor, produto["taxa_mensal"], meses)

        _rollback()

        acc.balance -= valor

        desc = (
            f"{produto['nome']} ({meses}m) | "
            f"Aplicação: R$ {valor:.2f} | "
            f"Rendimento esperado: R$ {rendimento:.2f} | "
            f"Montante: R$ {montante:.2f}"
        )

        _post_tx(acc.id, "Investimento", -valor, desc, acc.balance)
        db.session.commit()
        flash("Investimento realizado!", "success")
        return redirect(url_for("tx.investimentos"))

    investimentos = (
        Transaction.query.filter_by(account_id=acc.id, kind="Investimento")
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return render_template(
        "investimentos.html",
        produtos=produtos,
        investimentos=investimentos,
    )

@tx_bp.post("/investimentos/<int:inv_id>/resgatar")
def resgatar(inv_id: int):
    acc = _ensure_account()
    _rollback()

    inv = Transaction.query.filter_by(
        id=inv_id, account_id=acc.id, kind="Investimento"
    ).first()

    if not inv:
        flash("Investimento não encontrado.", "danger")
        return redirect(url_for("tx.investimentos"))

    valor_aplicado = _q(-inv.amount)
    meses = _parse_meses_descricao(inv.description)

    produto_nome = inv.description.split("(")[0].strip()
    produto = next((p for p in INV_PRODUTOS.values() if p["nome"] == produto_nome), None)

    if not produto:
        montante = valor_aplicado
        rendimento = _q(0)
    else:
        montante, rendimento = _simular_montante(valor_aplicado, produto["taxa_mensal"], meses)

    acc.balance += montante

    desc_resgate = (
        f"Resgate do investimento {inv.id} - {produto_nome} "
        f"({meses}m) | Principal: R$ {valor_aplicado:.2f} | "
        f"Rendimento: R$ {rendimento:.2f}"
    )

    _post_tx(acc.id, "Resgate", montante, desc_resgate, acc.balance)
    db.session.commit()
    flash("Resgate efetuado com sucesso.", "success")
    return redirect(url_for("tx.investimentos"))

@tx_bp.route("/emprestimo", methods=["GET", "POST"])
def emprestimo():
    if request.method == "POST":
        valor = _q(_to_float(request.form.get("valor", "0")))
        parcelas = request.form.get("meses", "0")
        acc = _ensure_account()
        _rollback()
        acc.balance += valor
        _post_tx(
            acc.id,
            "Empréstimo",
            valor,
            f"Empréstimo aprovado ({parcelas}x)",
            acc.balance,
        )
        db.session.commit()
        flash("Empréstimo aprovado.", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("emprestimo.html")
