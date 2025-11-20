from __future__ import annotations

import os
from pathlib import Path
from flask import Flask, send_from_directory

from .config import Config
from .extensions import db, migrate, login_manager, csrf
from .blueprints.auth import bp as auth_bp
from .blueprints.dashboard import bp as dash_bp
from .blueprints.transactions import bp as tx_bp
from .blueprints.profile import bp as profile_bp
from . import models  # garante modelos carregados p/ migrations

#alteração praticando aula 5

def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(
        __name__,
        instance_relative_config=True,          # instance/ relativo ao repo
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )

    # Garante a pasta instance/
    os.makedirs(app.instance_path, exist_ok=True)

    # Carrega config padrão
    app.config.from_object(config_class)

    # Define SQLite em instance/ se nada foi configurado externamente
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        db_path = Path(app.instance_path) / "tiger_bank.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path.as_posix()}"

    # Defaults seguros
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # Extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)

    # Dev helpers
    app.config.setdefault("SEND_FILE_MAX_AGE_DEFAULT", 0)
    app.config.setdefault("TEMPLATES_AUTO_RELOAD", True)
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
        return send_from_directory(static_dir, "favicon.ico", max_age=0)

    return app


# Exposto para wsgi:app e para flask run
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
