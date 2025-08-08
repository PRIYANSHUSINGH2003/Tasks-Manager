import json
import os
import tempfile
import pytest

from backend.app import create_app, db, Task, Comment


@pytest.fixture()
def app():
    # Use a temporary SQLite database per test session
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
    })

    yield app

    # Teardown
    with app.app_context():
        db.session.remove()
        db.drop_all()
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def task_id(app):
    with app.app_context():
        t = Task(title="Test Task", description="desc")
        db.session.add(t)
        db.session.commit()
        return t.id


def test_list_comments_initially_empty(client, task_id):
    resp = client.get(f"/api/tasks/{task_id}/comments")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["data"] == []


def test_create_comment_success(client, task_id):
    resp = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "First comment", "author": "alice"},
    )
    assert resp.status_code == 201
    data = resp.get_json()["data"]
    assert data["content"] == "First comment"
    assert data["author"] == "alice"
    assert data["task_id"] == task_id


def test_create_comment_validation(client, task_id):
    # Missing content
    resp = client.post(f"/api/tasks/{task_id}/comments", json={})
    assert resp.status_code == 400
    # Empty content
    resp = client.post(f"/api/tasks/{task_id}/comments", json={"content": "   "})
    assert resp.status_code == 400
    # Over length content
    resp = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "x" * 1001},
    )
    assert resp.status_code == 400


def test_update_comment_success(client, task_id):
    # Create
    create = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "c1", "author": "a1"},
    )
    cid = create.get_json()["data"]["id"]

    # Update content and author
    upd = client.put(
        f"/api/tasks/{task_id}/comments/{cid}",
        json={"content": "c2", "author": "bob"},
    )
    assert upd.status_code == 200
    d = upd.get_json()["data"]
    assert d["content"] == "c2"
    assert d["author"] == "bob"

    # Validate empty content rejected
    bad = client.put(
        f"/api/tasks/{task_id}/comments/{cid}",
        json={"content": "   "},
    )
    assert bad.status_code == 400


def test_delete_comment_success(client, task_id):
    create = client.post(
        f"/api/tasks/{task_id}/comments",
        json={"content": "to delete"},
    )
    cid = create.get_json()["data"]["id"]

    # Delete
    resp = client.delete(f"/api/tasks/{task_id}/comments/{cid}")
    assert resp.status_code == 200
    assert resp.get_json()["data"]["deleted"] is True

    # Ensure missing after delete
    missing = client.delete(f"/api/tasks/{task_id}/comments/{cid}")
    assert missing.status_code == 404


def test_comment_routes_require_existing_task(client):
    # Task 9999 does not exist
    resp = client.get("/api/tasks/9999/comments")
    assert resp.status_code == 404
    resp = client.post("/api/tasks/9999/comments", json={"content": "x"})
    assert resp.status_code == 404
    resp = client.put("/api/tasks/9999/comments/1", json={"content": "x"})
    assert resp.status_code == 404
    resp = client.delete("/api/tasks/9999/comments/1")
    assert resp.status_code == 404
