from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    chat_id: int

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None

class MessageInDB(MessageBase):
    id: int
    sender_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_read: bool = False
    is_deleted: bool = False

    class Config:
        orm_mode = True

class Message(MessageInDB):
    pass