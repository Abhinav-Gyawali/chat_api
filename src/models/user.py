from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

# Association table for user-chat many-to-many relationship
chat_users = Table(
    'chat_users',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('chat_id', Integer, ForeignKey('chats.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    # Basic fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)

    # Account status and metadata
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Real-time communication fields
    socket_id = Column(String, nullable=True)
    peer_id = Column(String, nullable=True)  # For WebRTC connections

    # Relationships
    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    owned_chats = relationship("Chat", 
                             back_populates="admin",
                             foreign_keys="Chat.admin_id",
                             cascade="all, delete-orphan")
    
    # Calls relationship
    initiated_calls = relationship("Call",
                                 back_populates="caller",
                                 foreign_keys="Call.caller_id",
                                 cascade="all, delete-orphan")
    received_calls = relationship("Call",
                                back_populates="receiver",
                                foreign_keys="Call.receiver_id",
                                cascade="all, delete-orphan")

    # Many-to-many relationship with chats
    chats = relationship(
        "Chat",
        secondary=chat_users,
        back_populates="participants"
    )

    class Config:
        orm_mode = True

    def __repr__(self):
        return f"<User {self.username}>"