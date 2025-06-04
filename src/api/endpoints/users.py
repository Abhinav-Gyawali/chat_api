from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ...models.user import User
from ...schemas.user import UserResponse
from ...core.security import get_current_user
from ..dependencies import get_db
from ...utils.image_handler import ImageHandler

router = APIRouter(prefix="/users", tags=["users"])

# Adding profile picture of user 
@router.post("/profile-picture", response_model=UserResponse)
async def upload_profile_picture(
    file: UploadFile = File(...),
    token_data = Depends(get_current_user),  # Changed parameter name
    db: Session = Depends(get_db)
):
    """
    Uploads a profile picture for the current user.
    
    Args:
        file (UploadFile): The image file to upload.
        token_data (TokenData): Token data containing username.
        db (Session): Database session dependency.
        
    Returns:
        User: The updated user object with the new profile picture URL.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    try:
        # Extract username from token_data
        username = token_data.username
        
        # Fetch user from database
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Save image using ImageHandler
        filename = await ImageHandler.save_profile_image(file, username)
        
        # Generate URL for the saved image
        image_url = ImageHandler.get_profile_image_url(filename)
        
        # Update user profile picture URL
        user.avatar = image_url
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file due to an internal error: {str(e)}")
    