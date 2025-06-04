from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base
import enum

class CallType(enum.Enum):
    VOICE = "voice"
    VIDEO = "video"

class CallStatus(enum.Enum):
    RINGING = "ringing"
    ONGOING = "ongoing"
    ENDED = "ended"
    MISSED = "missed"
    REJECTED = "rejected"

class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_type = Column(Enum(CallType))
    status = Column(Enum(CallStatus))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    
    caller_user = Column(String, ForeignKey("users.username"))
    receiver_user = Column(String, ForeignKey("users.username"))
    chat_id = Column(Integer, ForeignKey("chats.id"))
    
    caller = relationship("User", foreign_keys=[caller_user])
    receiver = relationship("User", foreign_keys=[receiver_user])
    chat = relationship("Chat")