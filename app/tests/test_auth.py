
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
from main import app
from connection import get_db

DATABASE_URL = "mysql+pymysql://root:admin1234@localhost:3310/palm"  # Use a test database

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_register(client):
    response = client.post("/api/v1/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Registration successful"

def test_login(client):
    response = client.post("/api/v1/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_password_reset(client):
    response = client.post("/api/v1/password_reset", json={
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset email sent"

def test_password_reset_confirm(client):
    # First, request a password reset to get the token
    response = client.post("/api/v1/password_reset", json={
        "email": "test@example.com"
    })
    reset_token = response.json()["reset_token"]

    # Now, confirm the password reset using the token
    response = client.post("/api/v1/password_reset/confirm", json={
        "token": reset_token,
        "new_password": "newtestpassword"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successful"

def test_logout(client):
    # First, login to get the access token
    response = client.post("/api/v1/login", json={
        "email": "test@example.com",
        "password": "newtestpassword"
    })
    access_token = response.json()["access_token"]

    # Now, logout using the access token
    response = client.post("/api/v1/logout", json={
        "token": access_token
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"