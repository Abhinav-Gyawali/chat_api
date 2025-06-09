from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import or_, and_, desc

from ..models.chat import Chat as ChatModel
from ..models.user import User as UserModel
from ..models.message import Message as MessageModel
from ..schemas.chat import ChatCreate, ChatUpdate, ChatResponse
from ..schemas.message import MessageCreate, MessageResponse

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def get_chat(self, chat_id: int) -> ChatModel:
        chat = self.db.query(ChatModel).filter(ChatModel.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    def get_user_chats(
        self, 
        username: str,
        limit: int = 20,
        search: Optional[str] = None,
        is_group: Optional[bool] = None,
        unread_only: bool = False
    ) -> List[ChatResponse]:
        """Get user's chats with filtering and pagination"""
        query = (
            self.db.query(ChatModel)
            .filter(ChatModel.users.any(username=username))
        )

        # Apply filters
        if search:
            query = query.filter(
                or_(
                    ChatModel.name.ilike(f"%{search}%"),
                    ChatModel.description.ilike(f"%{search}%")
                )
            )

        if is_group is not None:
            query = query.filter(ChatModel.is_group == is_group)

        # Get latest message for each chat
        chats = query.limit(limit).all()
        
        # Prepare response with additional data
        chat_responses = []
        for chat in chats:
            # Get last message
            last_message = (
                self.db.query(MessageModel)
                .filter(MessageModel.chat_id == chat.id)
                .order_by(desc(MessageModel.created_at))
                .first()
            )

            # Get unread count
            unread_count = (
                self.db.query(MessageModel)
                .filter(
                    and_(
                        MessageModel.chat_id == chat.id,
                        MessageModel.sender_user != username,
                        MessageModel.read_at.is_(None)
                    )
                )
                .count()
            )

            # Skip if unread_only is True and no unread messages
            if unread_only and unread_count == 0:
                continue

            # Convert to response model
            chat_response = ChatResponse(
                id=chat.id,
                name=chat.name,
                description=chat.description,
                is_group=chat.is_group,
                admin_user=chat.admin_user,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
                members=[user.username for user in chat.users],
                last_message={
                    "content": last_message.content if last_message else None,
                    "sender_username": last_message.sender_user if last_message else None,
                    "sent_at": last_message.created_at if last_message else None
                } if last_message else None,
                unread_count=unread_count
            )
            chat_responses.append(chat_response)

        return chat_responses

    async def send_message(
        self,
        chat_id: int,
        content: str,
        sender_username: str,
        message_type: str = "text",
        media_url: Optional[str] = None
    ) -> MessageResponse:
        """Send a new message in the chat"""
        # Verify chat exists and user is member
        chat = self.get_chat(chat_id)
        if not any(user.username == sender_username for user in chat.users):
            raise HTTPException(status_code=403, detail="Not a member of this chat")

        # Create message
        message = MessageModel(
            content=content,
            chat_id=chat_id,
            sender_user=sender_username,
            message_type=message_type,
            media_url=media_url,
            created_at=datetime.utcnow()
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # Update chat's updated_at timestamp
        chat.updated_at = datetime.utcnow()
        self.db.commit()

        return MessageResponse.from_orm(message)

    async def get_messages(
        self,
        chat_id: int,
        username: str,
        skip: int = 0,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[MessageResponse]:
        """Get chat messages with pagination"""
        # Verify chat exists and user is member
        chat = self.get_chat(chat_id)
        if not any(user.username == username for user in chat.users):
            raise HTTPException(status_code=403, detail="Not a member of this chat")

        # Build query
        query = (
            self.db.query(MessageModel)
            .filter(MessageModel.chat_id == chat_id)
        )

        if before:
            query = query.filter(MessageModel.created_at < before)

        messages = (
            query.order_by(desc(MessageModel.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [MessageResponse.from_orm(msg) for msg in messages]