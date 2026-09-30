import os
import time

from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


db = SQLAlchemy()


REQUEST_COUNT = Counter(
    "devforge_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "devforge_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


def create_app(config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devforge.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def record_metrics(response):
        duration = time.time() - request.start_time

        REQUEST_COUNT.labels(
            request.method,
            request.path,
            response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            request.method,
            request.path,
        ).observe(duration)

        return response

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
            "version": os.getenv("DEVFORGE_VERSION", "0.1.0")
        }

    @app.get("/metrics")
    def metrics():
        return Response(
            generate_latest(),
            mimetype=CONTENT_TYPE_LATEST,
        )

    return app
