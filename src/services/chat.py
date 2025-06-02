from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from ..models.chat import Chat as ChatModel
from ..models.user import User as UserModel
from ..schemas.chat import ChatCreate, ChatUpdate

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def get_chat(self, chat_id: int) -> ChatModel:
        chat = self.db.query(ChatModel).filter(ChatModel.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    def get_user_chats(self, user_id: int) -> List[ChatModel]:
        return (
            self.db.query(ChatModel)
            .filter(ChatModel.members.any(user_id))
            .all()
        )

    def create_chat(self, chat_data: ChatCreate, created_by: int) -> ChatModel:
        # Verify all members exist
        for member_id in chat_data.member_ids:
            if not self.db.query(UserModel).filter(UserModel.id == member_id).first():
                raise HTTPException(status_code=404, detail=f"User {member_id} not found")

        chat = ChatModel(
            name=chat_data.name,
            description=chat_data.description,
            is_group_chat=chat_data.is_group_chat,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        chat.members.extend(chat_data.member_ids)
        
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

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