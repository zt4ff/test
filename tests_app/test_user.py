from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_create_user():
    user_data = {
        "username": "testuser12",
        "email": "testmai32l@mail.com",
        "password": "testpassword"
    }
    response = client.post("/v1/users/register", json=user_data)
    assert response.status_code == 201

    