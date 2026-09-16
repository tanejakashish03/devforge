import os
from flask import Flask

app = Flask(__name__)


@app.get("/")
def home():
    return {"message": "Flask application is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port)
