
from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from tigerbank.extensions import db
from tigerbank.models import User, Account, AccountType
from tigerbank.security import hash_password, verify_password
from tigerbank.validators import is_valid_cpf, strong_password

bp = Blueprint("auth", __name__)

@bp.get("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return render_template("home.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = User.query.filter_by(email=email).first()
        if user and verify_password(password, user.password_hash):
            login_user(user)
            return redirect(url_for("dashboard.index"))
        flash("E-mail ou senha incorretos", "error")
    return render_template("login.html")

@bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        cpf = request.form.get("cpf","").strip()
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        confirm = request.form.get("confirm","")
        acc_type = request.form.get("acc_type","Corrente")
        if not is_valid_cpf(cpf):
            flash("CPF inválido", "error")
        elif password != confirm:
            flash("Senhas não coincidem", "error")
        elif not strong_password(password):
            flash("Senha fraca", "error")
        elif User.query.filter((User.cpf==cpf)|(User.email==email)).first():
            flash("CPF ou e-mail já cadastrado", "error")
        else:
            user = User(cpf=cpf, name=name, email=email, password_hash=hash_password(password))
            db.session.add(user)
            db.session.flush()
            acc = Account(user_id=user.id, type=acc_type, balance=0)
            db.session.add(acc)
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard.index"))
    return render_template("register.html")

@bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.home"))
