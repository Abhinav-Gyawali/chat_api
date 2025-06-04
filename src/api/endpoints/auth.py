from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from ...core.security import Token
from ...services.auth import AuthService
from ...schemas.user import UserCreate, User
from ...api.dependencies import get_db, get_current_user  # Added import

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return await AuthService.create_user(db, user_data)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        # Using form_data.username field for email since OAuth2PasswordRequestForm 
        # only provides username and password fields
        user = await AuthService.authenticate_user(
            db, form_data.username, form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = await AuthService.create_access_token_for_user(user)
        return Token(access_token=access_token, token_type="bearer")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login service error"
        )

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    access_token = await AuthService.create_access_token_for_user(current_user)
    return Token(access_token=access_token, token_type="bearer")