from datetime import timedelta
from typing import Optional
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..core.security import verify_password, get_password_hash, create_access_token
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin
from ..core.config import settings

class AuthService:
    @staticmethod
    async def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                logging.warning(f"Authentication failed: User not found for email {email}")
                return None
            
            if not verify_password(password, user.hashed_password):
                logging.warning(f"Authentication failed: Invalid password for user {email}")
                return None
            # 

            logging.info(f"User {email} authenticated successfully")
            return user
            
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )

    @staticmethod
    async def create_user(db: Session, user_data: UserCreate) -> User:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def create_access_token_for_user(user: User) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(
            data={"sub": str(user.username)},
            expires_delta=access_token_expires
        )