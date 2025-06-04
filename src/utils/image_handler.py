import os
from pathlib import Path
from fastapi import UploadFile
import aiofiles
from PIL import Image
from ..core.config import settings

class ImageHandler:
    UPLOAD_DIR = "uploads/profile_images"
    
    @classmethod
    async def save_profile_image(cls, file: UploadFile, username: str) -> str:
        """
        Save uploaded profile image to filesystem.
        
        Args:
            file (UploadFile): The uploaded image file
            username (str): Username to use in filename
            
        Returns:
            str: Filename of saved image
        """
        # Create upload directory if it doesn't exist
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
        
        # Generate filename using username
        file_extension = file.filename.split('.')[-1]
        filename = f"profile_{username}.{file_extension}"
        filepath = os.path.join(cls.UPLOAD_DIR, filename)
        
        # Save uploaded file
        async with aiofiles.open(filepath, 'wb') as f:
            content = await file.read()
            await f.write(content)
            
        # Optimize image
        cls._optimize_image(filepath)
        
        return filename

    @classmethod
    def get_profile_image_url(cls, filename: str) -> str:
        """
        Generate URL for accessing the profile image.
        
        Args:
            filename (str): Name of the image file
            
        Returns:
            str: URL path to access the image
        """
        return f"/static/profile_images/{filename}"

    @staticmethod
    def _optimize_image(filepath: str, max_size: tuple = (800, 800)):
        """
        Optimize the uploaded image by resizing and compressing.
        
        Args:
            filepath (str): Path to the image file
            max_size (tuple): Maximum width and height
        """
        try:
            with Image.open(filepath) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if larger than max size
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size)
                
                # Save optimized image
                img.save(filepath, 'JPEG', quality=85, optimize=True)
        except Exception as e:
            print(f"Error optimizing image: {str(e)}")