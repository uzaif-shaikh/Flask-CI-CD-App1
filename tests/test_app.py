import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_home_page_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"To-Do List" in res.data


def test_add_todo(client):
    res = client.post("/api/todos", json={"title": "Learn Jenkins"})
    assert res.status_code == 201
    assert res.get_json()["title"] == "Learn Jenkins"
    assert len(client.get("/api/todos").get_json()) == 1


def test_add_todo_requires_title(client):
    res = client.post("/api/todos", json={"title": "   "})
    assert res.status_code == 400


def test_toggle_todo(client):
    todo = client.post("/api/todos", json={"title": "Write Dockerfile"}).get_json()
    res = client.post(f"/api/todos/{todo['id']}/toggle")
    assert res.get_json()["done"] is True


def test_delete_todo(client):
    todo = client.post("/api/todos", json={"title": "Deploy to EC2"}).get_json()
    assert client.delete(f"/api/todos/{todo['id']}").status_code == 204
    assert client.get("/api/todos").get_json() == []


def test_missing_todo_returns_404(client):
    assert client.post("/api/todos/999/toggle").status_code == 404
    assert client.delete("/api/todos/999").status_code == 404
