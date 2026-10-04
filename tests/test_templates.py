import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "templates" / "projects"
TEMPLATES = ["flask", "fastapi", "node"]


def test_templates_have_ci_and_dependabot():
    for t in TEMPLATES:
        assert (ROOT / t / ".github/workflows/ci.yml").exists()
        assert (ROOT / t / ".github/dependabot.yml").exists()


def test_actions_use_major_version_tags_only():
    # Exact pins like @0.28.0 can disappear; major tags like @v4 float and
    # Dependabot keeps them current.
    for t in TEMPLATES:
        text = (ROOT / t / ".github/workflows/ci.yml").read_text()
        assert "trivy-action" not in text
        for ref in re.findall(r"uses:\s*\S+@(\S+)", text):
            assert re.fullmatch(r"v\d+", ref), f"{t}: unstable action ref {ref}"


def test_python_templates_install_pytest_in_ci():
    for t in ["flask", "fastapi"]:
        assert "pytest" in (ROOT / t / "requirements-dev.txt").read_text()
        assert "requirements-dev.txt" in (ROOT / t / ".github/workflows/ci.yml").read_text()
