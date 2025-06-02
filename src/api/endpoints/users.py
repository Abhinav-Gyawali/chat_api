from fastapi import APIRouter, Depends, UploadFile, File
from utils.image_handler import ImageHandler
from core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/me/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filename = await ImageHandler.save_profile_image(file, current_user.id)
    current_user.avatar = filename
    db.commit()
    
    return {
        "avatar_url": ImageHandler.get_profile_image_url(filename)
    }