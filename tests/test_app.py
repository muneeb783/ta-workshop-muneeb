import pytest

import app as app_module
from app import app


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task store before each test."""
    app_module.tasks.clear()
    app_module.tasks.extend([
        {"id": 1, "title": "Project-1 Report", "completed": False},
        {"id": 2, "title": "Project-2 MMFs", "completed": False}
    ])
    app_module.next_id = 3


def test_index(client):
    """Verify that the task tracker page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Verify that all tasks can be listed."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['completed'] is False for task in data)


def test_add_task_success(client):
    """Verify that a task is created with completed false by default."""
    response = client.post('/api/tasks', json={"title": "Test new task"})
    assert response.status_code == 201
    created_task = response.get_json()
    assert created_task['title'] == "Test new task"
    assert created_task['completed'] is False

    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


def test_add_task_with_completed_value(client):
    """Verify that an explicitly supplied completion value is retained."""
    response = client.post(
        '/api/tasks',
        json={"title": "Finished task", "completed": True}
    )
    assert response.status_code == 201
    assert response.get_json()['completed'] is True


def test_add_task_missing_title(client):
    """Verify that creating a task without a title fails."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()

    response = client.post('/api/tasks', json={})
    assert response.status_code == 400


def test_update_task_success(client):
    """Verify that a task can be marked complete and incomplete."""
    response = client.patch('/api/tasks/1', json={"completed": True})
    assert response.status_code == 200
    assert response.get_json()['id'] == 1
    assert response.get_json()['completed'] is True

    response = client.patch('/api/tasks/1', json={"completed": False})
    assert response.status_code == 200
    assert response.get_json()['completed'] is False


def test_update_missing_task(client):
    """Verify that updating an unknown task returns a not-found error."""
    response = client.patch('/api/tasks/999', json={"completed": True})
    assert response.status_code == 404
    assert response.get_json() == {"error": "Task not found"}


def test_update_task_requires_completed_value(client):
    """Verify that PATCH requests must include completed."""
    response = client.patch('/api/tasks/1', json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Completed is required"}


def test_update_task_rejects_non_boolean_value(client):
    """Verify that completed must be a JSON boolean."""
    response = client.patch('/api/tasks/1', json={"completed": "true"})
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Completed must be a boolean"
    }


def test_delete_task(client):
    """Verify that an existing task can be deleted."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200

    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
