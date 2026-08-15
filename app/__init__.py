from flask import Flask


def create_app():
    app = Flask(__name__)

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