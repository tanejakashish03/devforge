from types import SimpleNamespace

from app import create_app
import app.routes.projects as projects_module


def test_dashboard(client):
    response = client.get("/")

    assert response.status_code == 200


def test_create_project_page(client):
    response = client.get("/projects/create")

    assert response.status_code == 200


def test_create_project_saves_template(client, app):
    response = client.post(
        "/projects/create",
        data={
            "name": "fastapi-test",
            "repository_name": "fastapi-test",
            "application": "fastapi",
            "visibility": "private",
            "port": "8000",
            "health_endpoint": "/health",
            "environment": "development",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        from app.models.project import Project

        project = Project.query.filter_by(
            name="fastapi-test"
        ).first()

        assert project is not None
        assert project.application == "fastapi"
        assert project.template_type == "fastapi"


def test_create_project_rejects_invalid_template(client):
    response = client.post(
        "/projects/create",
        data={
            "name": "invalid-test",
            "repository_name": "invalid-test",
            "application": "django",
            "visibility": "private",
            "port": "8000",
            "health_endpoint": "/health",
            "environment": "development",
        },
    )

    assert response.status_code == 400


def test_existing_github_repository_shows_existing_page(
    client,
    monkeypatch,
):
    project = SimpleNamespace(
        id=1,
        name="Existing Project",
        repository_name="existing-project",
        visibility="private",
        github_repo_url=None,
        github_repo_id=None,
        template_type="flask",
    )

    repository = {
        "id": 123,
        "name": "existing-project",
        "html_url": (
            "https://github.com/test-user/existing-project"
        ),
        "owner": {
            "login": "test-user",
        },
    }

    def fake_get(model, project_id):
        return project

    def fake_create_repository(
        name,
        description,
        private,
    ):
        return {
            "status": "exists",
            "repository": repository,
        }

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    monkeypatch.setattr(
        projects_module,
        "create_repository",
        fake_create_repository,
    )

    response = client.post(
        "/projects/1/github"
    )

    assert response.status_code == 200

    assert b"Repository Already Exists" in response.data
    assert b"Open Existing Repository" in response.data
    assert (
        b"https://github.com/test-user/existing-project"
        in response.data
    )

    # Existing repository must not automatically be linked.
    assert project.github_repo_id is None
    assert project.github_repo_url is None


def test_link_existing_github_repository(
    client,
    monkeypatch,
):
    project = SimpleNamespace(
        id=1,
        name="Existing Project",
        repository_name="existing-project",
        visibility="private",
        github_repo_url=None,
        github_repo_id=None,
        template_type="flask",
    )

    repository = {
        "id": 123,
        "name": "existing-project",
        "html_url": (
            "https://github.com/test-user/existing-project"
        ),
        "owner": {
            "login": "test-user",
        },
    }

    def fake_get(model, project_id):
        return project

    def fake_get_authenticated_user():
        return {
            "login": "test-user",
        }

    def fake_get_repository(
        owner,
        repository_name,
    ):
        assert owner == "test-user"
        assert repository_name == "existing-project"

        return repository

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
        "get_authenticated_user",
        fake_get_authenticated_user,
    )

    monkeypatch.setattr(
        projects_module,
        "get_repository",
        fake_get_repository,
    )

    response = client.post(
        "/projects/1/github/link"
    )

    assert response.status_code == 302
    assert "github=linked" in response.location

    assert project.github_repo_id == 123
    assert project.github_repo_url == (
        "https://github.com/test-user/existing-project"
    )


def test_discard_project_does_not_delete_github_repository(
    client,
    monkeypatch,
):
    project = SimpleNamespace(
        id=1,
        name="Existing Project",
        repository_name="existing-project",
        visibility="private",
        github_repo_url=None,
        github_repo_id=None,
        template_type="flask",
    )

    deleted = []

    def fake_get(model, project_id):
        return project

    def fake_delete(project_to_delete):
        deleted.append(project_to_delete)

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "delete",
        fake_delete,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "commit",
        lambda: None,
    )

    response = client.post(
        "/projects/1/github/discard"
    )

    assert response.status_code == 302
    assert "github=discarded" in response.location

    assert deleted == [project]

    # The GitHub repository is never accessed or deleted.
    assert project.github_repo_id is None
    assert project.github_repo_url is None

def test_delete_project_only(
    client,
    monkeypatch,
):
    project = SimpleNamespace(
        id=1,
        name="Test Project",
        repository_name="test-project",
        github_repo_url=(
            "https://github.com/test-user/test-project"
        ),
        github_repo_id=123,
    )

    deleted_projects = []

    def fake_get(model, project_id):
        return project

    def fake_delete(project_to_delete):
        deleted_projects.append(project_to_delete)

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "delete",
        fake_delete,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "commit",
        lambda: None,
    )

    def github_delete_should_not_run(*args, **kwargs):
        assert False, (
            "GitHub repository should not be deleted"
        )

    monkeypatch.setattr(
        projects_module,
        "delete_repository",
        github_delete_should_not_run,
    )

    response = client.post(
        "/projects/1/delete",
        data={
            "delete_github": "false",
        },
    )

    assert response.status_code == 302

    assert "github=discarded" in response.location

    assert project in deleted_projects

def test_delete_project_and_github_repository(
    client,
    monkeypatch,
):
    project = SimpleNamespace(
        id=1,
        name="Test Project",
        repository_name="test-project",
        github_repo_url=(
            "https://github.com/test-user/test-project"
        ),
        github_repo_id=123,
    )

    deleted_projects = []
    deleted_repositories = []

    def fake_get(model, project_id):
        return project

    def fake_delete(project_to_delete):
        deleted_projects.append(project_to_delete)

    def fake_get_authenticated_user():
        return {
            "login": "test-user",
        }

    def fake_delete_repository(
        owner,
        repository_name,
    ):
        deleted_repositories.append(
            (owner, repository_name)
        )

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "delete",
        fake_delete,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "commit",
        lambda: None,
    )

    monkeypatch.setattr(
        projects_module,
        "get_authenticated_user",
        fake_get_authenticated_user,
    )

    monkeypatch.setattr(
        projects_module,
        "delete_repository",
        fake_delete_repository,
    )

    response = client.post(
        "/projects/1/delete",
        data={
            "delete_github": "true",
        },
    )

    assert response.status_code == 302
    assert "github=deleted" in response.location

    assert deleted_repositories == [
        ("test-user", "test-project")
    ]

    assert deleted_projects == [project]

def test_delete_project_kept_when_github_deletion_fails(
    client,
    monkeypatch,
):
    project = SimpleNamespace(
        id=1,
        name="Test Project",
        repository_name="test-project",
        github_repo_url=(
            "https://github.com/test-user/test-project"
        ),
        github_repo_id=123,
    )

    deleted_projects = []

    def fake_get(model, project_id):
        return project

    def fake_delete(project_to_delete):
        deleted_projects.append(project_to_delete)

    def fake_get_authenticated_user():
        return {
            "login": "test-user",
        }

    def fake_delete_repository(
        owner,
        repository_name,
    ):
        raise RuntimeError(
            "GitHub repository deletion failed"
        )

    monkeypatch.setattr(
        projects_module.db.session,
        "get",
        fake_get,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "delete",
        fake_delete,
    )

    monkeypatch.setattr(
        projects_module.db.session,
        "commit",
        lambda: None,
    )

    monkeypatch.setattr(
        projects_module,
        "get_authenticated_user",
        fake_get_authenticated_user,
    )

    monkeypatch.setattr(
        projects_module,
        "delete_repository",
        fake_delete_repository,
    )

    response = client.post(
        "/projects/1/delete",
        data={
            "delete_github": "true",
        },
    )

    assert response.status_code == 302

    assert "github=delete_failed" in response.location

    assert project not in deleted_projects

def test_create_project_rejects_duplicate_repository_name(
    client,
    app,
):
    client.post(
        "/projects/create",
        data={
            "name": "existing-project",
            "repository_name": "existing-project",
            "application": "flask",
            "visibility": "private",
            "port": "5000",
            "health_endpoint": "/health",
            "environment": "development",
        },
    )

    response = client.post(
        "/projects/create",
        data={
            "name": "another-project",
            "repository_name": "existing-project",
            "application": "fastapi",
            "visibility": "private",
            "port": "8000",
            "health_endpoint": "/health",
            "environment": "development",
        },
    )

    assert response.status_code == 409

    assert (
        b"A project with this repository name already exists"
        in response.data
    )