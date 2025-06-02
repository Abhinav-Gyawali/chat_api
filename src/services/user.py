from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

from ..models.user import User as UserModel
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> UserModel:
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return self.db.query(UserModel).offset(skip).limit(limit).all()

    def create_user(self, user_data: UserCreate) -> UserModel:
        if self.get_user_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(user_data.password)
        user = UserModel(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_online=False,
            last_seen=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserModel:
        user = self.get_user(user_id)
        
        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
        for field, value in update_data.items():
            setattr(user, field, value)
            
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_seen(self, user_id: int) -> UserModel:
        user = self.get_user(user_id)
        user.last_seen = datetime.utcnow()
        self.db.commit()
        return user

    def set_online_status(self, user_id: int, is_online: bool) -> UserModel:
        user = self.get_user(user_id)
        user.is_online = is_online
        user.last_seen = datetime.utcnow()
        self.db.commit()
        return user