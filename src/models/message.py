from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
import enum

class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    VOICE_NOTE = "voice_note"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    media_url = Column(String, nullable=True)
    media_thumbnail = Column(String, nullable=True)
    media_duration = Column(Integer, nullable=True)  # For audio/video duration in seconds
    media_size = Column(Integer, nullable=True)  # File size in bytes
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User")