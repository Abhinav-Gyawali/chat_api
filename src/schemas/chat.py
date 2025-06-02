from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_group_chat: bool = False

class ChatCreate(ChatBase):
    member_ids: List[int]

class ChatUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_group_chat: Optional[bool] = None

class ChatInDB(ChatBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Chat(ChatInDB):
    members: List[int]