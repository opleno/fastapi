from app import schemas
from .database import client, session # session fixture is also needed as client makes use of it

def test_root(client):
    response = client.get("/")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "¡¡¡Hola Mundo!!!"}


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "hello@outlook.com", "password": "1234"})
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "hello@outlook.com"
    assert res.status_code == 201
