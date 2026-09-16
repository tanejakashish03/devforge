import importlib.util
from pathlib import Path


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"

spec = importlib.util.spec_from_file_location("flask_template_app", APP_PATH)
flask_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flask_app)

app = flask_app.app


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json == {"message": "Flask application is running"}


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "healthy"}
