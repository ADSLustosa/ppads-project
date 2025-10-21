from __future__ import annotations
from pathlib import Path
from flask import Flask, send_from_directory
from config import Config

# IMPORTS CORRETOS (pacote interno)
from tigerbank.tigerbank.extensions import db, migrate, login_manager, csrf
from tigerbank.tigerbank.blueprints.auth import bp as auth_bp
from tigerbank.tigerbank.blueprints.dashboard import bp as dash_bp
from tigerbank.tigerbank.blueprints.transactions import bp as tx_bp
from tigerbank.tigerbank.blueprints.profile import bp as profile_bp
from tigerbank.tigerbank import models as _models  # garante modelos p/ migrations

def create_app(config_class: type = Config) -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="tigerbank/templates",
        static_folder="tigerbank/static",
    )
    app.config.from_object(config_class)

    # Extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)

    # Dev helpers
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(tx_bp)
    app.register_blueprint(profile_bp)

    # Healthcheck
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # Favicon para evitar 404 no log
    @app.get("/favicon.ico")
    def favicon():
        static_dir = Path(app.static_folder)
        return send_from_directory(str(static_dir), "favicon.ico", max_age=0)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
