import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'


def test_get_tasks_empty(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_task(client):
    task_data = {'title': 'Test Task', 'description': 'A test task'}
    response = client.post('/api/tasks', json=task_data)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == 'Test Task'
    assert data['description'] == 'A test task'
    assert 'id' in data


def test_create_task_missing_title(client):
    task_data = {'description': 'Task without title'}
    response = client.post('/api/tasks', json=task_data)
    assert response.status_code == 400


def test_complete_task(client):
    task_data = {'title': 'Complete Me', 'description': 'Task to complete'}
    response = client.post('/api/tasks', json=task_data)
    task = response.json()
    task_id = task['id']

    response = client.patch(f'/api/tasks/{task_id}/complete')
    assert response.status_code == 200
    data = response.json()
    assert data['completed'] == True


def test_complete_nonexistent_task(client):
    response = client.patch('/api/tasks/9999/complete')
    assert response.status_code == 404


def test_delete_task(client):
    task_data = {'title': 'Delete Me', 'description': 'Task to delete'}
    response = client.post('/api/tasks', json=task_data)
    task = response.json()
    task_id = task['id']

    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200

    response = client.get('/api/tasks')
    tasks = response.json()
    task_ids = [t['id'] for t in tasks]
    assert task_id not in task_ids


def test_delete_nonexistent_task(client):
    response = client.delete('/api/tasks/9999')
    assert response.status_code == 404


def test_get_tasks_after_creation(client):
    client.post('/api/tasks', json={'title': 'Task 1', 'description': 'First'})
    client.post('/api/tasks', json={'title': 'Task 2', 'description': 'Second'})

    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
