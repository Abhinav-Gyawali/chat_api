from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base
from .associations import chat_users

class User(Base):
    __tablename__ = "users"

    # Basic fields
    username = Column(String, primary_key=True , index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
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
                             foreign_keys="Chat.admin_user",
                             cascade="all, delete-orphan")
    
    # Calls relationship
    initiated_calls = relationship("Call",
                                 back_populates="caller",
                                 foreign_keys="Call.caller_user",
                                 cascade="all, delete-orphan")
    received_calls = relationship("Call",
                                back_populates="receiver",
                                foreign_keys="Call.receiver_user",
                                cascade="all, delete-orphan")

    # Many-to-many relationship with chats
    administered_chats = relationship(
        "Chat",
        foreign_keys="Chat.admin_user",
        overlaps="owned_chats"  # Add this line
    )
    chats = relationship("Chat", secondary=chat_users, back_populates="users")

    class Config:
        from_attributes = True


    def __repr__(self):
        return f"<User {self.username}>"