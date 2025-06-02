import pytest
from fastapi import status
from src.core.security import create_access_token

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}

def test_create_chat(client, test_user, auth_headers):
    response = client.post(
        "/chats/",
        headers=auth_headers,
        json={
            "name": "New Chat",
            "description": "New Chat Description",
            "is_group_chat": False,
            "member_ids": [test_user.id]
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Chat"

def test_get_chat(client, test_chat, auth_headers):
    response = client.get(
        f"/chats/{test_chat.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_chat.id

def test_update_chat(client, test_chat, auth_headers):
    response = client.patch(
        f"/chats/{test_chat.id}",
        headers=auth_headers,
        json={"name": "Updated Chat Name"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Chat Name"

def test_delete_chat(client, test_chat, auth_headers):
    response = client.delete(
        f"/chats/{test_chat.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_get_user_chats(client, test_chat, auth_headers):
    response = client.get(
        "/chats/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1