from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.endpoints import auth, ws, users  # Add users import
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
app.include_router(users.router, prefix=settings.API_V1_STR)  # Add this line

# Mount the media directory
app.mount("/media", StaticFiles(directory="media"), name="media")
# Mount the uploads directory
app.mount("/static", StaticFiles(directory="uploads"), name="static")

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Chat API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)