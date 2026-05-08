import pytest
import json
from backend.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_get_tasks_empty(client):
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_create_task(client):
    task_data = {'title': 'Test Task', 'description': 'A test task'}
    response = client.post('/api/tasks',
                          data=json.dumps(task_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Task'
    assert data['description'] == 'A test task'
    assert 'id' in data


def test_create_task_missing_title(client):
    task_data = {'description': 'Task without title'}
    response = client.post('/api/tasks',
                          data=json.dumps(task_data),
                          content_type='application/json')
    assert response.status_code == 400


def test_complete_task(client):
    task_data = {'title': 'Complete Me', 'description': 'Task to complete'}
    response = client.post('/api/tasks',
                          data=json.dumps(task_data),
                          content_type='application/json')
    task = json.loads(response.data)
    task_id = task['id']

    response = client.patch(f'/api/tasks/{task_id}/complete')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['completed'] == True


def test_complete_nonexistent_task(client):
    response = client.patch('/api/tasks/9999/complete')
    assert response.status_code == 404


def test_delete_task(client):
    task_data = {'title': 'Delete Me', 'description': 'Task to delete'}
    response = client.post('/api/tasks',
                          data=json.dumps(task_data),
                          content_type='application/json')
    task = json.loads(response.data)
    task_id = task['id']

    response = client.delete(f'/api/tasks/{task_id}')
    assert response.status_code == 200

    response = client.get('/api/tasks')
    tasks = json.loads(response.data)
    task_ids = [t['id'] for t in tasks]
    assert task_id not in task_ids


def test_delete_nonexistent_task(client):
    response = client.delete('/api/tasks/9999')
    assert response.status_code == 404


def test_get_tasks_after_creation(client):
    client.post('/api/tasks',
                data=json.dumps({'title': 'Task 1', 'description': 'First'}),
                content_type='application/json')
    client.post('/api/tasks',
                data=json.dumps({'title': 'Task 2', 'description': 'Second'}),
                content_type='application/json')

    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) >= 2
