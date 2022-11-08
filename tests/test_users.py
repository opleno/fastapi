import pytest
from jose import jwt

from app import schemas
# session fixture is also needed, as client makes use of it
from .database import client, session
from app.config import settings


@pytest.fixture
def test_user(client):
    user_data = {"email": "hello@outlook.com", "password": "1234"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    print(res.json())
    new_user = res.json()
    new_user['password'] = user_data["password"]
    return new_user


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


def test_login_user(client, test_user):
    res = client.post(
        "/login", data={"username": test_user["email"], "password": test_user["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.oauth2_secret_key, [settings.algorithm])
    id = payload.get("user_id")

    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200
