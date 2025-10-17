
from __future__ import annotations
from flask import Flask
from config import Config
from tigerbank.extensions import db, migrate, login_manager, csrf
from tigerbank.blueprints.auth import bp as auth_bp
from tigerbank.blueprints.dashboard import bp as dash_bp
from tigerbank.blueprints.transactions import bp as tx_bp
from tigerbank.blueprints.profile import bp as profile_bp
from tigerbank import models

def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True, template_folder="tigerbank/templates", static_folder="tigerbank/static")
    app.config.from_object(config_class)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(tx_bp)
    app.register_blueprint(profile_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    if __name__ == '__main__':
        app.run(debug=True)

    return app

app = create_app()
