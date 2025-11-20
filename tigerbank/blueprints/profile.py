from __future__ import annotations
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from tigerbank.extensions import db
from tigerbank.models import User
from tigerbank.security import verify_password, hash_password
from tigerbank.validators import strong_password

bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/perfil",
    template_folder="../templates",
)


# ===============================================================
# VISUALIZAÇÃO
# ===============================================================
@bp.get("/", endpoint="view")
@login_required
def view():
    return render_template("perfil.html", user=current_user)


# ===============================================================
# ATUALIZAÇÃO DE PERFIL
# ===============================================================
@bp.post("/atualizar", endpoint="update")
@login_required
def atualizar():
    try:
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        senha_atual = request.form.get("senha_atual") or ""

        # -------- valida senha atual --------
        if not verify_password(senha_atual, current_user.password_hash):
            flash("Senha atual incorreta.", "error")
            return redirect(url_for("profile.view"))

        # -------- valida e-mail duplicado --------
        if email:
            exists = User.query.filter(
                User.email == email,
                User.id != current_user.id
            ).first()

            if exists:
                flash("E-mail já está em uso.", "error")
                return redirect(url_for("profile.view"))

        # -------- aplica alterações --------
        changed = False

        if name and name != current_user.name:
            current_user.name = name
            changed = True

        if email and email != current_user.email:
            current_user.email = email
            changed = True

        if not changed:
            flash("Nada foi alterado.", "info")
            return redirect(url_for("profile.view"))

        db.session.commit()
        flash("Perfil atualizado com sucesso.", "success")
        return redirect(url_for("profile.view"))

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao atualizar o perfil: {e}", "error")
        return redirect(url_for("profile.view"))


# ===============================================================
# ALTERAÇÃO DE SENHA
# ===============================================================
@bp.post("/senha", endpoint="change_password")
@login_required
def alterar_senha():
    try:
        atual = request.form.get("atual") or ""
        nova = request.form.get("nova") or ""
        conf = request.form.get("conf") or ""

        # -------- valida senha atual --------
        if not verify_password(atual, current_user.password_hash):
            flash("Senha atual incorreta.", "error")

        # -------- valida igualdade --------
        elif nova != conf:
            flash("As senhas não coincidem.", "error")

        # -------- valida força da senha --------
        elif not strong_password(nova):
            flash("Senha fraca. Use letras maiúsculas, minúsculas, números e símbolos.", "error")

        else:
            current_user.password_hash = hash_password(nova)
            db.session.commit()
            flash("Senha alterada com sucesso.", "success")

        return redirect(url_for("profile.view"))

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao alterar a senha: {e}", "error")
        return redirect(url_for("profile.view"))
