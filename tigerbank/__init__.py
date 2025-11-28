# tigerbank/__init__.py

from flask import Flask
from tigerbank.config import Config
from tigerbank.extensions import db, migrate, login_manager, csrf

def create_app():
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Importa e registra blueprints
    from tigerbank.blueprints.auth import auth_bp
    from tigerbank.blueprints.dashboard import dashboard_bp
    from tigerbank.blueprints.transactions import tx_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tx_bp)

    return app
