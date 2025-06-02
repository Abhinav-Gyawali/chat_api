import pytest
from fastapi import status
from src.core.security import create_access_token

def test_login_success(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_user):
    access_token = create_access_token({"sub": str(test_user.id)})
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == test_user.email