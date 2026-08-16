from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devforge.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Register application routes
    from app.routes.main import main_bp
    from app.routes.projects import projects_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)

    # Create database tables
    with app.app_context():
        from app.models.project import Project
        db.create_all()

    @app.get("/")
    def home():
        return "DevForge is running!"

    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "service": "devforge"
        }

    @app.get("/version")
    def version():
        return {
            "service": "devforge",
            "version": "0.1.0"
        }

    return app