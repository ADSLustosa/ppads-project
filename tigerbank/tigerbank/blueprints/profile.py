
from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from tigerbank.extensions import db
from tigerbank.models import User
from tigerbank.security import verify_password, hash_password

bp = Blueprint("profile", __name__, url_prefix="/perfil")

@bp.get("/")
@login_required
def view():
    return render_template("perfil.html")

@bp.post("/atualizar")
@login_required
def atualizar():
    name = request.form.get("name","").strip()
    email = request.form.get("email","").strip().lower()
    senha_atual = request.form.get("senha_atual","")
    if not verify_password(senha_atual, current_user.password_hash):
        flash("Senha atual incorreta", "error"); return redirect(url_for("profile.view"))
    if email and User.query.filter(User.email==email, User.id!=current_user.id).first():
        flash("E-mail já em uso", "error"); return redirect(url_for("profile.view"))
    current_user.name = name or current_user.name
    current_user.email = email or current_user.email
    db.session.commit()
    flash("Perfil atualizado", "success")
    return redirect(url_for("profile.view"))

@bp.post("/senha")
@login_required
def alterar_senha():
    atual = request.form.get("atual","")
    nova = request.form.get("nova","")
    conf = request.form.get("conf","")
    if not verify_password(atual, current_user.password_hash):
        flash("Senha atual incorreta", "error")
    elif nova != conf:
        flash("Senhas não coincidem", "error")
    else:
        current_user.password_hash = hash_password(nova)
        db.session.commit()
        flash("Senha alterada", "success")
    return redirect(url_for("profile.view"))
