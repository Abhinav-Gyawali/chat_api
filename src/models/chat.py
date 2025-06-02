from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

chat_users = Table(
    "chat_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("chat_id", Integer, ForeignKey("chats.id")),
)

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)  # Optional for group chats
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_group = Column(Boolean, default=False)
    group_avatar = Column(String, nullable=True)
    
    # For group chats
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    description = Column(String, nullable=True)
    
    messages = relationship("Message", back_populates="chat", order_by="Message.created_at")
    participants = relationship("User", secondary=chat_users, backref="chats")
    calls = relationship("Call", back_populates="chat")