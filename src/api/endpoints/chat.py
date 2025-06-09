from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from ..dependencies import get_db, get_current_user
from ...models.chat import Chat
from ...services.chat import ChatService
from ...schemas.chat import ChatResponse, ChatCreate, ChatUpdate

router = APIRouter(prefix="/chats", tags=["chat"])

@router.post("/", response_model=ChatResponse, status_code=201)
def create_chat(
    chat: ChatCreate, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new chat.

    Parameters:
    - For group chats: name, description (optional), member_usernames
    - For direct chats: only member_username required
    """
    try:
        chat_service = ChatService(db)
        return chat_service.create_chat(
            chat_data=chat,
            created_by=current_user.username
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ChatResponse])
def get_chats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_group: Optional[bool] = None,
    unread_only: bool = False
):
    """
    Get user's chats with filtering and pagination.

    Parameters:
    - limit: Maximum number of chats to return
    - search: Search chats by name
    - is_group: Filter by group/direct chats
    - unread_only: Show only chats with unread messages
    """
    try:
        chat_service = ChatService(db)
        return chat_service.get_user_chats(
            username=current_user.username,
            limit=limit,
            search=search,
            is_group=is_group,
            unread_only=unread_only
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int = Path(..., description="The ID of the chat to get"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat by ID"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    if current_user.username not in [member.username for member in chat.users]:
        raise HTTPException(status_code=403, detail="Not a member of this chat")
    return chat

@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    chat_update: ChatUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update chat settings (group chats only)"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id)
    if chat.admin_user != current_user.username:
        raise HTTPException(status_code=403, detail="Only admin can update chat")
    return await chat_service.update_chat(chat_id, chat_update)

@router.post("/{chat_id}/members/", response_model=ChatResponse)
async def add_members(
    chat_id: int,
    member_usernames: list[str],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add new members to a group chat"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id)
    if not chat.is_group:
        raise HTTPException(status_code=400, detail="Cannot add members to direct chat")
    if chat.admin_user != current_user.username:
        raise HTTPException(status_code=403, detail="Only admin can add members")
    return await chat_service.add_members(chat_id, member_usernames)

@router.delete("/{chat_id}/members/{username}")
async def remove_member(
    chat_id: int,
    username: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from a group chat"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id)
    if not chat.is_group:
        raise HTTPException(status_code=400, detail="Cannot remove members from direct chat")
    if chat.admin_user != current_user.username:
        raise HTTPException(status_code=403, detail="Only admin can remove members")
    await chat_service.remove_member(chat_id, username)
    return {"message": "Member removed successfully"}