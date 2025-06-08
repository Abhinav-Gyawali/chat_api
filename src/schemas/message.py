from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    VOICE_NOTE = "voice_note"

class MessageBase(BaseModel):
    content: str
    chat_id: int

class MessageCreate(MessageBase):
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None

class MessageInDB(MessageBase):
    id: int
    sender_user: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_type: MessageType
    media_url: Optional[str] = None
    media_thumbnail: Optional[str] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageResponse(MessageInDB):
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    is_sender_online: Optional[bool] = False
    
    class Config:
        from_attributes = True
        
        # Example JSON Schema
        json_schema_extra = {
            "example": {
                "id": 1,
                "chat_id": 1,
                "content": "Hello everyone!",
                "message_type": "text",
                "sender_user": "john_doe",
                "sender_name": "John Doe",
                "sender_avatar": "/static/profile_images/john_doe.jpg",
                "is_sender_online": True,
                "created_at": "2025-06-05T10:00:00",
                "updated_at": "2025-06-05T10:00:00",
                "delivered_at": "2025-06-05T10:00:01",
                "read_at": "2025-06-05T10:00:02",
                "media_url": None,
                "media_thumbnail": None
            }
        }