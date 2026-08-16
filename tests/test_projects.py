from app import create_app


def test_dashboard(client):
    response = client.get("/")

    assert response.status_code == 200


def test_create_project_page(client):
    response = client.get("/projects/create")

    assert response.status_code == 200