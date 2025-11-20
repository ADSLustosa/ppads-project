from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from tigerbank.extensions import db
from tigerbank.models import User, Account
from tigerbank.security import hash_password, verify_password
from tigerbank.validators import strong_password, normalize_digits

bp = Blueprint("auth", __name__, template_folder="../templates")


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        # validação compatível com hash antigo e bcrypt
        if user and verify_password(password, user.password_hash):
            login_user(user)
            return redirect(url_for("dashboard.index"))

        flash("E-mail ou senha incorretos.", "error")

    return render_template("login.html")


# ---------------------------------------------------------
# REGISTRO
# ---------------------------------------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        cpf_raw = request.form.get("cpf", "")
        cpf = normalize_digits(cpf_raw)

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        acc_type = request.form.get("acc_type", "Corrente")

        # ------ validações ------
        if password != confirm:
            flash("Senhas não coincidem.", "error")

        elif not strong_password(password):
            flash("Senha fraca. Use letras maiúsculas, minúsculas, números e símbolos.", "error")

        elif User.query.filter((User.cpf == cpf) | (User.email == email)).first():
            flash("CPF ou e-mail já cadastrado.", "error")

        else:
            # cria usuário
            user = User(
                cpf=cpf,
                name=name,
                email=email,
                password_hash=hash_password(password)
            )
            db.session.add(user)
            db.session.flush()  # garante ID antes de criar a conta

            # cria conta bancária
            acc = Account(
                user_id=user.id,
                type=acc_type,
                balance=0,
            )
            db.session.add(acc)
            db.session.commit()

            # loga automaticamente
            login_user(user)
            return redirect(url_for("dashboard.index"))

    return render_template("register.html")


# ---------------------------------------------------------
# RECUPERAÇÃO DE SENHA
# ---------------------------------------------------------
@bp.route("/esqueci-minha-senha", methods=["GET", "POST"], endpoint="esqueci_senha")
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        # neste projeto acadêmico, não enviamos e-mail real
        flash("Se o e-mail existir, enviaremos instruções de redefinição.", "success")
        return redirect(url_for("auth.login"))

    return render_template("esqueci_senha.html")


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
