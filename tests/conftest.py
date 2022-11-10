

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pytest
# from alembic import command

from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models

# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:1234@localhost:5432/fastapi_test"
# _test
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host_uri}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # another option, with alembic instead of sqlalchemy:
    # command.downgrade("base")
    # command.upgrade("head")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    # Dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "hello@outlook.com", "password": "1234"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "hello2@outlook.com", "password": "1234"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authenticated_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def preloaded_posts(test_user, test_user2, session):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user['id']
        }, {
            "title": "2nd title",
            "content": "2nd content",
            "owner_id": test_user['id']
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user['id']
        }
        , {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user2['id']
        }
    ]

    def cast_post(post):
        return models.Post(**post)

    posts_map = map(cast_post, posts_data)
    posts = list(posts_map)

    session.add_all(posts)
    # session.add_all([models.Post(title="first title",
    #                              content="first content",
    #                              owner_id=test_user['id']),
    #                 models.Post(title="2nd title",
    #                             content="2nd content",
    #                             owner_id=test_user['id']),
    #                 models.Post(title="3d title",
    #                             content="3d content",
    #                             owner_id=test_user['id']),
    #                  ])
    session.commit()
    posts_in_db = session.query(models.Post).all()
    
    return posts_in_db
