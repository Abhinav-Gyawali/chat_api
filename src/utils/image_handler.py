import os
from PIL import Image
from fastapi import UploadFile, HTTPException
from core.config import settings
import uuid

class ImageHandler:
    @staticmethod
    async def save_profile_image(file: UploadFile, user_id: int) -> str:
        """Save and process profile image"""
        if not file.content_type in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(400, "Invalid image type")
            
        if file.size > settings.MAX_PROFILE_IMAGE_SIZE:
            raise HTTPException(400, "Image too large")
            
        # Create directory if not exists
        profile_dir = os.path.join(settings.MEDIA_ROOT, settings.PROFILE_IMAGES_DIR)
        os.makedirs(profile_dir, exist_ok=True)
        
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(profile_dir, filename)
        
        # Save and process image
        try:
            image = Image.open(file.file)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if larger than max dimensions
            if image.width > settings.PROFILE_IMAGE_MAX_WIDTH or \
               image.height > settings.PROFILE_IMAGE_MAX_HEIGHT:
                image.thumbnail((
                    settings.PROFILE_IMAGE_MAX_WIDTH,
                    settings.PROFILE_IMAGE_MAX_HEIGHT
                ))
            
            # Save original
            image.save(filepath, quality=85, optimize=True)
            
            # Create thumbnail
            thumbnail_path = os.path.join(
                profile_dir, 
                f"thumb_{filename}"
            )
            image.thumbnail(settings.PROFILE_THUMBNAIL_SIZE)
            image.save(thumbnail_path, quality=85, optimize=True)
            
            return filename
            
        except Exception as e:
            raise HTTPException(500, "Error processing image")

    @staticmethod
    def get_profile_image_url(filename: str) -> str:
        """Get the full URL for a profile image"""
        if not filename:
            filename = settings.DEFAULT_PROFILE_IMAGE
            
        if settings.MEDIA_BASE_URL:
            return f"{settings.MEDIA_BASE_URL}/{settings.PROFILE_IMAGES_DIR}/{filename}"
        return f"/{settings.MEDIA_ROOT}/{settings.PROFILE_IMAGES_DIR}/{filename}"