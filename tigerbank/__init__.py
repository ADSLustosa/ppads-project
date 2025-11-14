# tigerbank/__init__.py
from __future__ import annotations
import os
from flask import Flask, Response, render_template
from tigerbank.extensions import db, login_manager
from tigerbank.models import User

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Config base
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-in-dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///tigerbank.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True


    # Extensões
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

    # Blueprints
    from tigerbank.blueprints import auth, dashboard, transactions, profile
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(profile.bp)

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
        
    # --- Registro do filtro CPF ---
    @app.template_filter("cpf")
    def format_cpf(value: str):
        digits = ''.join(filter(str.isdigit, value or ""))
        if len(digits) != 11:
            return value
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"


    return app
