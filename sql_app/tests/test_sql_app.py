import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_create_user(client):
    response = client.post(
        "/signup/",
        json={"email": "example@example.com", "password": "example", "name": "test"},
    )
    assert response.status_code == 200, response.text


def test_create_user_with_same_email(client):
    response = client.post(
        "/signup/",
        json={"email": "example@example.com", "password": "example", "name": "test"},
    )
    data = response.json()
    assert data["detail"] == "Email already registered"


def test_login(client):
    response = client.post("/login/?email=example%40example.com&password=example")
    data = response.json()
    assert data["Details"] == "User logged in successfully"


def test_login_invalid(client):
    response = client.post("/login/?email=example%40example.com&password=examples")
    data = response.json()
    assert data["Details"] == "Please enter valid credentials"
