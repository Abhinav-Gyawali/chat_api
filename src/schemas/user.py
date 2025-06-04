from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    username: str
    is_active: bool
    is_online: bool
    last_seen: datetime
    created_at: datetime
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    avatar: str | None = None

    class Config:
        from_attributes = True
