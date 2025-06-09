from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.endpoints import auth, ws, users, chat
from .db.base import Base, engine
from .models.associations import chat_users
from .models.user import User
from .models.chat import Chat
from .models.message import Message
from .models.call import Call
from fastapi.staticfiles import StaticFiles


# Create database tables
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

Base.metadata.create_all(bind=engine)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(ws.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)  # Add this line
app.include_router(users.router, prefix=settings.API_V1_STR)  # Add this line

# Mount the media directory
# Mount the uploads directory
app.mount("/static", StaticFiles(directory="uploads", html=True), name="static")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Create required directories
import os
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Chat API"}

