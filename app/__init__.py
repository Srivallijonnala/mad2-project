from datetime import timedelta
from flask import Flask

from app.config import Config
from app.extensions import db, cache


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.permanent_session_lifetime = timedelta(hours=8)

    db.init_app(app)
    cache.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.company import company_bp
    from app.routes.student import student_bp
    from app.routes.pages import pages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(pages_bp)

    return app
