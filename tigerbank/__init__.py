from flask import Flask
from tigerbank.config import Config
from tigerbank.extensions import db, migrate, login_manager, csrf

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from tigerbank.blueprints.auth import auth_bp
    from tigerbank.blueprints.dashboard import dashboard_bp
    from tigerbank.blueprints.transactions import bp as tx_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tx_bp)

    return app
