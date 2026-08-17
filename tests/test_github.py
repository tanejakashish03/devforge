from types import SimpleNamespace

import app.routes.projects as projects_module


def test_create_github_repository(client, monkeypatch):
    project = SimpleNamespace(
        id=1,
        name="Test Project",
        repository_name="test-project",
        visibility="private",
        github_repo_url=None,
        github_repo_id=None,
    )

    def fake_get(model, project_id):
        return project

    def fake_create_repository(name, description, private):
        assert name == "test-project"
        assert description == "DevForge project: Test Project"
        assert private is True

        return {
            "id": 123456789,
            "name": "test-project",
            "html_url": "https://github.com/test/test-project",
        }

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "commit",
        lambda: None,
    )

    monkeypatch.setattr(
        projects_module,
        "create_repository",
        fake_create_repository,
    )

    response = client.post("/projects/1/github")

    assert response.status_code == 302
    assert "github=created" in response.location

    assert project.github_repo_id == 123456789
    assert project.github_repo_url == (
        "https://github.com/test/test-project"
    )


def test_create_github_repository_project_not_found(
    client,
    monkeypatch,
):
    def fake_get(model, project_id):
        return None

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    response = client.post("/projects/999/github")

    assert response.status_code == 404

    assert response.json == {
        "error": "Project not found"
    }


def test_create_github_repository_already_exists(
    client,
    monkeypatch,
):
    project = SimpleNamespace(
        id=1,
        name="Existing Project",
        repository_name="existing-project",
        visibility="private",
        github_repo_url="https://github.com/test/existing-project",
        github_repo_id=987654321,
    )

    def fake_get(model, project_id):
        return project

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    response = client.post("/projects/1/github")

    assert response.status_code == 302
    assert "github=exists" in response.location