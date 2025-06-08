from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base
from .associations import chat_users


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # Making it nullable for direct chats
    admin_user = Column(String, ForeignKey("users.username"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_group = Column(Boolean, default=False)
    group_avatar = Column(String, nullable=True)
    description = Column(String, nullable=True)

    # For group chats

    admin = relationship("User", foreign_keys=[admin_user], back_populates="administered_chats")
    users = relationship("User", secondary=chat_users, back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    calls = relationship("Call", back_populates="chat")