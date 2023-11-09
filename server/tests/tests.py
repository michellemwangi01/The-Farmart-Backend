import pytest
from api import  app  # Import your User model and SQLAlchemy db instance
from flask import json


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_get_users(client):
    response = client.get('users/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)