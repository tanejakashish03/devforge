from types import SimpleNamespace
import base64

import pytest

import app.routes.projects as projects_module


def test_create_github_repository(client, monkeypatch):
    project = SimpleNamespace(
        id=1,
        name="Test Project",
        repository_name="test-project",
        visibility="private",
        github_repo_url=None,
        github_repo_id=None,
        template_type="flask",
    )

    def fake_get(model, project_id):
        return project

    def fake_create_repository(name, description, private):
        assert name == "test-project"
        assert description == "DevForge project: Test Project"
        assert private is True

        return {
            "status": "created",
            "repository": {
                "id": 123456789,
                "name": "test-project",
                "html_url": "https://github.com/test/test-project",
                "owner": {
                    "login": "test",
                },
            },
        }

    def fake_upload_project_directory(
        owner,
        repository_name,
        source_directory,
    ):
        assert owner == "test"
        assert repository_name == "test-project"

        return [
            "app.py",
            "requirements.txt",
            "README.md",
        ]

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

    monkeypatch.setattr(
        projects_module,
        "upload_project_directory",
        fake_upload_project_directory,
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


def test_upload_file_to_repository(monkeypatch):
    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-token",
    )

    from app.services.github_service import (
        upload_file_to_repository,
    )

    class FakeGetResponse:
        status_code = 404

        text = "Not Found"

    class FakePutResponse:
        status_code = 201

        def json(self):
            return {
                "content": {
                    "name": "README.md"
                }
            }

    def fake_get(*args, **kwargs):
        return FakeGetResponse()

    def fake_put(*args, **kwargs):
        assert (
            kwargs["json"]["content"]
            == base64.b64encode(
                b"# Test Project"
            ).decode("utf-8")
        )

        assert (
            kwargs["headers"]["Authorization"]
            == "Bearer test-token"
        )

        assert kwargs["json"]["message"] == "Add README.md"

        assert "sha" not in kwargs["json"]

        return FakePutResponse()

    monkeypatch.setattr(
        "app.services.github_service.requests.get",
        fake_get,
    )

    monkeypatch.setattr(
        "app.services.github_service.requests.put",
        fake_put,
    )

    result = upload_file_to_repository(
        owner="test-user",
        repository_name="test-repo",
        file_path="README.md",
        content="# Test Project",
    )

    assert result["content"]["name"] == "README.md"


def test_upload_file_to_repository_updates_existing_file(
    monkeypatch,
):
    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-token",
    )

    from app.services.github_service import (
        upload_file_to_repository,
    )

    class FakeGetResponse:
        status_code = 200
        text = "OK"

        def json(self):
            return {
                "name": "README.md",
                "sha": "existing-file-sha",
            }

    class FakePutResponse:
        status_code = 200

        def json(self):
            return {
                "content": {
                    "name": "README.md"
                }
            }

    def fake_get(*args, **kwargs):
        return FakeGetResponse()

    def fake_put(*args, **kwargs):
        assert kwargs["json"]["sha"] == "existing-file-sha"

        assert (
            kwargs["json"]["content"]
            == base64.b64encode(
                b"# Updated Project"
            ).decode("utf-8")
        )

        return FakePutResponse()

    monkeypatch.setattr(
        "app.services.github_service.requests.get",
        fake_get,
    )

    monkeypatch.setattr(
        "app.services.github_service.requests.put",
        fake_put,
    )

    result = upload_file_to_repository(
        owner="test-user",
        repository_name="test-repo",
        file_path="README.md",
        content="# Updated Project",
    )

    assert result["content"]["name"] == "README.md"


def test_upload_file_to_repository_rejects_github_error(
    monkeypatch,
):
    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-token",
    )

    from app.services.github_service import (
        upload_file_to_repository,
    )

    class FakeGetResponse:
        status_code = 404
        text = "Not Found"

    class FakePutResponse:
        status_code = 500
        text = "Internal Server Error"

    def fake_get(*args, **kwargs):
        return FakeGetResponse()

    def fake_put(*args, **kwargs):
        return FakePutResponse()

    monkeypatch.setattr(
        "app.services.github_service.requests.get",
        fake_get,
    )

    monkeypatch.setattr(
        "app.services.github_service.requests.put",
        fake_put,
    )

    with pytest.raises(RuntimeError, match="GitHub file upload failed"):
        upload_file_to_repository(
            owner="test-user",
            repository_name="test-repo",
            file_path="README.md",
            content="# Test Project",
        )


def test_create_repository_uses_existing_repository(
    monkeypatch,
):
    class FakeResponse:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self._data = data
            self.text = str(data)

        def json(self):
            return self._data

    post_response = FakeResponse(
        422,
        {
            "errors": [
                {
                    "field": "name",
                    "message": "name already exists on this account",
                }
            ]
        },
    )

    user_response = FakeResponse(
        200,
        {
            "login": "test-user",
        },
    )

    repository_response = FakeResponse(
        200,
        {
            "id": 123,
            "name": "existing-repo",
            "html_url": (
                "https://github.com/test-user/existing-repo"
            ),
            "owner": {
                "login": "test-user",
            },
        },
    )

    post_responses = [post_response]
    get_responses = [
        user_response,
        repository_response,
    ]

    def fake_post(*args, **kwargs):
        return post_responses.pop(0)

    def fake_get(*args, **kwargs):
        return get_responses.pop(0)

    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-token",
    )

    monkeypatch.setattr(
        "app.services.github_service.requests.post",
        fake_post,
    )

    monkeypatch.setattr(
        "app.services.github_service.requests.get",
        fake_get,
    )

    from app.services.github_service import create_repository

    result = create_repository(
        name="existing-repo",
        description="Test repository",
        private=True,
    )

    assert result["status"] == "exists"
    assert result["repository"]["id"] == 123
    assert result["repository"]["html_url"] == (
        "https://github.com/test-user/existing-repo"
    )


def test_delete_repository(monkeypatch):
    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-token",
    )

    from app.services.github_service import (
        delete_repository,
    )

    class FakeResponse:
        status_code = 204
        text = ""

    def fake_delete(*args, **kwargs):

        assert (
            args[0]
            == "https://api.github.com/repos/"
            "test-user/test-repo"
        )

        assert (
            kwargs["headers"]["Authorization"]
            == "Bearer test-token"
        )

        return FakeResponse()

    monkeypatch.setattr(
        "app.services.github_service.requests.delete",
        fake_delete,
    )

    result = delete_repository(
        owner="test-user",
        repository_name="test-repo",
    )

    assert result is True


def test_delete_repository_rejects_github_error(
    monkeypatch,
):
    monkeypatch.setenv(
        "GITHUB_TOKEN",
        "test-token",
    )

    from app.services.github_service import (
        delete_repository,
    )

    class FakeResponse:
        status_code = 403
        text = "Forbidden"

    def fake_delete(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.github_service.requests.delete",
        fake_delete,
    )

    try:

        delete_repository(
            owner="test-user",
            repository_name="test-repo",
        )

        assert False, "Expected RuntimeError"

    except RuntimeError as error:

        assert (
            "GitHub repository deletion failed"
            in str(error)
        )