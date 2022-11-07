from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pytest
# from alembic import command

from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base

# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:1234@localhost:5432/fastapi_test"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host_uri}_test"

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
