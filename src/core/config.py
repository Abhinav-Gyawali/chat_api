from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Tuple, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Chat API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your-super-secret-key"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000000
    DATABASE_URL: str = "sqlite:///./chat.db"

    # Database settings
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./chat.db"
    DB_ECHO_LOG: bool = False

    MEDIA_ROOT: str = "media"
    PROFILE_IMAGES_DIR: str = "profile_images"
    CHAT_MEDIA_DIR: str = "chat_media"
    
    # Image settings
    MAX_PROFILE_IMAGE_SIZE: int = 5_242_880  # 5MB in bytes
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
    DEFAULT_PROFILE_IMAGE: str = "default.png"
    
    # Image dimensions
    PROFILE_IMAGE_MAX_WIDTH: int = 800
    PROFILE_IMAGE_MAX_HEIGHT: int = 800
    PROFILE_THUMBNAIL_SIZE: Tuple[int, int] = (150, 150)
    
    # CDN or storage URL (if using external storage)
    MEDIA_BASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()