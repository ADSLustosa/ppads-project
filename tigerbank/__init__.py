from __future__ import annotations
from flask import Flask, Response, render_template
from tigerbank.extensions import db, login_manager
from tigerbank.models import User
from tigerbank.config import Config, TestConfig


def create_app(testing: bool = False) -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Carregar configuração
    if testing:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    # Inicializa extensões
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

    # Registro de Blueprints
    from tigerbank.blueprints import auth, dashboard, transactions, profile
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(profile.bp)

    # Rota padrão
    @app.route("/")
    def index():
        return render_template("home.html")

    @app.route("/favicon.ico")
    def favicon():
        try:
            return app.send_static_file("favicon.ico")
        except Exception:
            return Response(status=204)

    # Segurança contra sessões inconsistentes
    @app.before_request
    def _rollback_defensivo():
        try:
            db.session.rollback()
        except:
            pass

    @app.teardown_request
    def _teardown_request(exc):
        try:
            if exc:
                db.session.rollback()
        finally:
            db.session.remove()

    return app
