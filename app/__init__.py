from flask import Flask
from config import Config
from .extensions import db, login_manager
from .extensions import db, login_manager, csrf, migrate
from .blueprints.main import main_bp
from .blueprints.auth import auth_bp
from .blueprints.admin import admin_bp
from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Enregistrement des blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Contexte global pour les templates
    @app.context_processor
    def inject_now():
        return {'current_year': datetime.utcnow().year}

    return app


