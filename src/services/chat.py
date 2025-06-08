from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from ..models.chat import Chat as ChatModel
from ..models.user import User as UserModel
from ..schemas.chat import ChatCreate, ChatUpdate, ChatResponse

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def get_chat(self, chat_id: int) -> ChatModel:
        chat = self.db.query(ChatModel).filter(ChatModel.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    def get_user_chats(self, username: str) -> List[ChatModel]:
        return (
            self.db.query(ChatModel)
            .filter(ChatModel.members.any(username))
            .all()
        )

    def create_chat(self, chat_data: ChatCreate, created_by: str) -> ChatModel:
        """
        Create a new chat with given members.
        """
        # Use set for unique usernames
        member_usernames = set(chat_data.member_usernames)
        member_usernames.add(created_by)  # Add creator
        
        # Verify all members exist and collect unique user objects
        users = []
        seen_usernames = set()
        
        for username in member_usernames:
            if username in seen_usernames:
                continue
            
            user = self.db.query(UserModel).filter(UserModel.username == username).first()
            if not user:
                raise HTTPException(status_code=404, detail=f"User {username} not found")
                
            users.append(user)
            seen_usernames.add(username)

        # Create chat
        chat = ChatModel(
            name=chat_data.name if chat_data.is_group else None,
            description=chat_data.description,
            is_group=chat_data.is_group,
            admin_user=created_by if chat_data.is_group else None,
            created_at=datetime.utcnow()
        )

        # Add unique users
        chat.users.extend(users)
        
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        
        # Prepare response data
        return ChatResponse(
            id=chat.id,
            name=chat.name,
            description=chat.description,
            is_group=chat.is_group,
            admin_user=chat.admin_user,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            members=[user.username for user in chat.users],
            last_message=None,
            unread_count=0
        )

    def update_chat(self, chat_id: int, chat_data: ChatUpdate) -> ChatModel:
        chat = self.get_chat(chat_id)
        
        for field, value in chat_data.dict(exclude_unset=True).items():
            setattr(chat, field, value)
        
        chat.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def delete_chat(self, chat_id: int) -> None:
        chat = self.get_chat(chat_id)
        self.db.delete(chat)
        self.db.commit()