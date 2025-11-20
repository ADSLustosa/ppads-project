# tigerbank/__init__.py
from __future__ import annotations
import os
from flask import Flask, Response, render_template
from .extensions import db, login_manager
from .models import User
from tigerbank.config import Config

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # 1️⃣ Carrega TODA a config primeiro
    app.config.from_object(Config)

    # 2️⃣ Inicializa extensões DEPOIS da Config
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # 3️⃣ Blueprints
    from tigerbank.blueprints import auth, dashboard, transactions, profile
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(profile.bp)

    # 4️⃣ Rotas básicas
    @app.route("/")
    def index():
        return render_template("home.html")

    @app.before_request
    def _rollback_defensivo():
        try:
            db.session.rollback()
        except Exception:
            pass

    @app.teardown_request
    def _teardown_request(exc):
        try:
            if exc is not None:
                db.session.rollback()
        finally:
            db.session.remove()

    @app.route("/favicon.ico")
    def favicon():
        try:
            return app.send_static_file("favicon.ico")
        except Exception:
            return Response(status=204)

    # 5️⃣ Filtro de CPF
    @app.template_filter("cpf")
    def format_cpf(value: str):
        digits = ''.join(filter(str.isdigit, value or ""))
        if len(digits) != 11:
            return value
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"

    return app
