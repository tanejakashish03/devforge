import pytest

from app.services.generator_service import generate_project


def test_generate_flask_project(tmp_path):
    destination = tmp_path / "flask-project"

    generate_project(
        template_type="flask",
        destination=destination,
    )

    assert (destination / "app.py").exists()
    assert (destination / "requirements.txt").exists()
    assert (destination / "README.md").exists()


def test_generate_fastapi_project(tmp_path):
    destination = tmp_path / "fastapi-project"

    generate_project(
        template_type="fastapi",
        destination=destination,
    )

    assert (destination / "main.py").exists()
    assert (destination / "requirements.txt").exists()
    assert (destination / "README.md").exists()


def test_generate_node_project(tmp_path):
    destination = tmp_path / "node-project"

    generate_project(
        template_type="node",
        destination=destination,
    )

    assert (destination / "src" / "index.js").exists()
    assert (destination / "package.json").exists()
    assert (destination / "README.md").exists()


def test_invalid_template_is_rejected(tmp_path):
    destination = tmp_path / "invalid-project"

    with pytest.raises(ValueError):
        generate_project(
            template_type="invalid",
            destination=destination,
        )


def test_generate_project_includes_ci_workflow(tmp_path):
    destination = tmp_path / "flask-project"

    generate_project(
        template_type="flask",
        destination=destination,
    )

    workflow = (
        destination
        / ".github"
        / "workflows"
        / "ci.yml"
    )

    test_file = (
        destination
        / "tests"
        / "test_flask_app.py"
    )

    assert workflow.exists()
    assert test_file.exists()

    workflow_content = workflow.read_text()

    assert "Flask CI" in workflow_content
    assert "pytest" in workflow_content


def test_fastapi_project_includes_ci_workflow(tmp_path):
    destination = tmp_path / "fastapi-project"

    generate_project(
        template_type="fastapi",
        destination=destination,
    )

    workflow = (
        destination
        / ".github"
        / "workflows"
        / "ci.yml"
    )

    test_file = (
        destination
        / "tests"
        / "test_fastapi_app.py"
    )

    assert workflow.exists()
    assert test_file.exists()

    workflow_content = workflow.read_text()

    assert "FastAPI CI" in workflow_content
    assert "pytest" in workflow_content


def test_node_project_includes_ci_workflow(tmp_path):
    destination = tmp_path / "node-project"

    generate_project(
        template_type="node",
        destination=destination,
    )

    workflow = (
        destination
        / ".github"
        / "workflows"
        / "ci.yml"
    )

    test_file = (
        destination
        / "tests"
        / "index.test.js"
    )

    package_file = destination / "package.json"
    lock_file = destination / "package-lock.json"

    assert workflow.exists()
    assert test_file.exists()
    assert package_file.exists()
    assert lock_file.exists()

    workflow_content = workflow.read_text()

    assert "Node CI" in workflow_content
    assert "npm ci" in workflow_content
    assert "npm test" in workflow_content


def test_flask_project_includes_jenkins_and_gitlab_ci(tmp_path):
    destination = tmp_path / "flask-project"

    generate_project(
        template_type="flask",
        destination=destination,
    )

    jenkinsfile = destination / "Jenkinsfile"
    gitlab_ci = destination / ".gitlab-ci.yml"

    assert jenkinsfile.exists()
    assert gitlab_ci.exists()

    jenkins_content = jenkinsfile.read_text()
    gitlab_content = gitlab_ci.read_text()

    assert "Install Dependencies" in jenkins_content
    assert "pytest" in jenkins_content

    assert "pipeline {" in jenkins_content
    assert "agent any" in jenkins_content

    assert "python:3.12" in gitlab_content
    assert "pytest" in gitlab_content

    assert "stages:" in gitlab_content
    assert "test:" in gitlab_content


def test_fastapi_project_includes_jenkins_and_gitlab_ci(tmp_path):
    destination = tmp_path / "fastapi-project"

    generate_project(
        template_type="fastapi",
        destination=destination,
    )

    jenkinsfile = destination / "Jenkinsfile"
    gitlab_ci = destination / ".gitlab-ci.yml"

    assert jenkinsfile.exists()
    assert gitlab_ci.exists()

    jenkins_content = jenkinsfile.read_text()
    gitlab_content = gitlab_ci.read_text()

    assert "Install Dependencies" in jenkins_content
    assert "pytest" in jenkins_content

    assert "pipeline {" in jenkins_content
    assert "agent any" in jenkins_content

    assert "python:3.12" in gitlab_content
    assert "pytest" in gitlab_content

    assert "stages:" in gitlab_content
    assert "test:" in gitlab_content


def test_node_project_includes_jenkins_and_gitlab_ci(tmp_path):
    destination = tmp_path / "node-project"

    generate_project(
        template_type="node",
        destination=destination,
    )

    jenkinsfile = destination / "Jenkinsfile"
    gitlab_ci = destination / ".gitlab-ci.yml"

    assert jenkinsfile.exists()
    assert gitlab_ci.exists()

    jenkins_content = jenkinsfile.read_text()
    gitlab_content = gitlab_ci.read_text()

    assert "npm ci" in jenkins_content
    assert "npm test" in jenkins_content

    assert "pipeline {" in jenkins_content
    assert "agent any" in jenkins_content

    assert "node:24" in gitlab_content
    assert "npm ci" in gitlab_content
    assert "npm test" in gitlab_content

    assert "stages:" in gitlab_content
    assert "test:" in gitlab_content