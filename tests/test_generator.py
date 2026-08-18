from pathlib import Path

import pytest

from app.services.generator_service import generate_project


def test_generate_flask_project(tmp_path):
    destination = tmp_path / "flask-project"

    generate_project("flask", destination)

    assert (destination / "app.py").exists()
    assert (destination / "requirements.txt").exists()
    assert (destination / "README.md").exists()


def test_generate_fastapi_project(tmp_path):
    destination = tmp_path / "fastapi-project"

    generate_project("fastapi", destination)

    assert (destination / "main.py").exists()
    assert (destination / "requirements.txt").exists()
    assert (destination / "README.md").exists()


def test_generate_node_project(tmp_path):
    destination = tmp_path / "node-project"

    generate_project("node", destination)

    assert (destination / "src" / "index.js").exists()
    assert (destination / "package.json").exists()
    assert (destination / "README.md").exists()


def test_invalid_template_is_rejected(tmp_path):
    destination = tmp_path / "invalid-project"

    with pytest.raises(ValueError):
        generate_project("invalid", destination)