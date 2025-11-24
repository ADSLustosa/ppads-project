# tigerbank/__init__.py
from __future__ import annotations
import os
from flask import Flask, Response, render_template
from tigerbank.extensions import db, login_manager
from tigerbank.models import User


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    is_dev = os.environ.get("FLASK_ENV") == "development"

    app.config["TEMPLATES_AUTO_RELOAD"] = is_dev
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0 if is_dev else None
    if is_dev:
        app.jinja_env.auto_reload = True


    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-in-dev")

    db_url = os.environ.get("DATABASE_URL", "sqlite:///tigerbank.db")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


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

    from tigerbank.blueprints import auth, dashboard, transactions, profile
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(profile.bp)


    @app.route("/")
    def index():
        return render_template("home.html")

    @app.route("/favicon.ico")
    def favicon():
        try:
            return app.send_static_file("favicon.ico")
        except Exception:
            return Response(status=204)


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

    return app
