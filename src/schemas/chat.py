from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_group: bool = False

class ChatCreate(ChatBase):
    member_usernames: List[str]

class ChatUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_group: Optional[bool] = None

class ChatInDB(ChatBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    id: int
    name: Optional[str]  # Make name optional since it can be None for direct chats
    description: Optional[str]
    is_group: bool
    admin_user: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    members: List[str]  # Will contain usernames
    last_message: Optional[dict] = None
    unread_count: Optional[int] = 0

    class Config:
        from_attributes = True
        
        # Example JSON Schema
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Project Discussion",
                "description": "Chat for discussing project updates",
                "is_group": True,
                "admin_user": "ram",
                "created_at": "2025-06-05T10:00:00",
                "updated_at": "2025-06-05T10:00:00",
                "members": ["ram", "hari", "shyam"],
                "last_message": {
                    "content": "Hello team!",
                    "sender_username": "ram",
                    "sent_at": "2025-06-05T10:00:00"
                },
                "unread_count": 0
            }
        }