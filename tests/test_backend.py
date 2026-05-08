import sys
import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app, tasks, task_id_counter


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the task list before each test to ensure isolation."""
    tasks.clear()
    global task_id_counter
    import backend.main
    backend.main.task_id_counter = 1
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """Get authentication headers with valid JWT token."""
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint(client):
    """Test the health check endpoint returns healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_auth_token_success(client):
    """Test successful authentication with valid credentials."""
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_auth_token_invalid_credentials(client):
    """Test authentication fails with invalid credentials."""
    response = client.post(
        "/api/auth/token",
        data={"username": "wronguser", "password": "wrongpass"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Incorrect username or password" in data["detail"]


def test_get_tasks_empty(client, auth_headers):
    """Test getting tasks when none exist returns empty list."""
    response = client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_tasks_with_auth(client, auth_headers):
    """Test that tasks endpoint requires authentication."""
    # First, create a task with auth
    client.post(
        "/api/tasks",
        json={"title": "Test task"},
        headers=auth_headers
    )
    # Then get tasks with auth
    response = client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Test task"


def test_get_tasks_without_auth(client):
    """Test that tasks endpoint returns 401 without authentication."""
    response = client.get("/api/tasks")
    assert response.status_code == 401


def test_create_task_success(client, auth_headers):
    """Test creating a new task with authentication."""
    response = client.post(
        "/api/tasks",
        json={"title": "New task"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New task"
    assert data["completed"] == False
    assert "id" in data


def test_create_task_without_auth(client):
    """Test that creating a task without auth returns 401."""
    response = client.post(
        "/api/tasks",
        json={"title": "New task"}
    )
    assert response.status_code == 401


def test_create_multiple_tasks(client, auth_headers):
    """Test creating multiple tasks assigns unique IDs."""
    response1 = client.post(
        "/api/tasks",
        json={"title": "Task 1"},
        headers=auth_headers
    )
    response2 = client.post(
        "/api/tasks",
        json={"title": "Task 2"},
        headers=auth_headers
    )
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["id"] != response2.json()["id"]


def test_complete_task_success(client, auth_headers):
    """Test marking a task as completed."""
    # Create a task first
    create_response = client.post(
        "/api/tasks",
        json={"title": "Task to complete"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Mark it as complete
    response = client.put(
        f"/api/tasks/{task_id}/complete",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] == True
    assert data["id"] == task_id


def test_complete_task_not_found(client, auth_headers):
    """Test completing a non-existent task returns 404."""
    response = client.put(
        "/api/tasks/999/complete",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_complete_task_without_auth(client):
    """Test that completing a task without auth returns 401."""
    response = client.put("/api/tasks/1/complete")
    assert response.status_code == 401


def test_delete_task_success(client, auth_headers):
    """Test deleting a task successfully."""
    # Create a task first
    create_response = client.post(
        "/api/tasks",
        json={"title": "Task to delete"},
        headers=auth_headers
    )
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(
        f"/api/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Verify task is deleted
    get_response = client.get("/api/tasks", headers=auth_headers)
    tasks = get_response.json()
    assert len(tasks) == 0


def test_delete_task_not_found(client, auth_headers):
    """Test deleting a non-existent task returns 404."""
    response = client.delete(
        "/api/tasks/999",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_task_without_auth(client):
    """Test that deleting a task without auth returns 401."""
    response = client.delete("/api/tasks/1")
    assert response.status_code == 401


def test_task_lifecycle(client, auth_headers):
    """Test complete task lifecycle: create, complete, and delete."""
    # Create task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Lifecycle task"},
        headers=auth_headers
    )
    assert create_response.status_code == 200
    task = create_response.json()
    task_id = task["id"]

    # Verify task exists
    get_response = client.get("/api/tasks", headers=auth_headers)
    tasks = get_response.json()
    assert len(tasks) == 1

    # Complete task
    complete_response = client.put(
        f"/api/tasks/{task_id}/complete",
        headers=auth_headers
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["completed"] == True

    # Delete task
    delete_response = client.delete(
        f"/api/tasks/{task_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 200

    # Verify task is gone
    get_response = client.get("/api/tasks", headers=auth_headers)
    tasks = get_response.json()
    assert len(tasks) == 0
