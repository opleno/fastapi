import pytest
from jose import jwt

from app import schemas
# session fixture is also needed, as client makes use of it
from app.config import settings


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

@pytest.mark.parametrize("username, password, status_code", [
    ('wrongemail@gmail.com', '1234', 403),
    ('hello@outlook.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, '1234', 422),
    ('hello@outlook.com', None, 422)
])
def test_login_incorrect_user(client, username, password, status_code):
    res = client.post(
        "/login", data={"username": username, "password": password})

    assert res.status_code == status_code
    # assert res.json().get('detail') == 'Invalid credentials'
