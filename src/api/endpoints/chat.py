from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ...models.chat import Chat
from ...models.message import Message
from ...schemas.chat import ChatCreate, ChatResponse
from ...schemas.message import MessageCreate, MessageResponse
from ...services.chat import ChatService

router = APIRouter(prefix="/chats", tags=["chat"])
chat_service = ChatService()

@router.post("/chats/", response_model=ChatResponse)
def create_chat(chat: ChatCreate, db: Session = Depends(get_db)):
    return chat_service.create_chat(db=db, chat=chat)

@router.get("/chats/", response_model=list[ChatResponse])
def get_chats(db: Session = Depends(get_db)):
    return chat_service.get_chats(db=db)

@router.post("/chats/{chat_id}/messages/", response_model=MessageResponse)
def send_message(chat_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    return chat_service.send_message(db=db, chat_id=chat_id, message=message)

@router.get("/chats/{chat_id}/messages/", response_model=list[MessageResponse])
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    return chat_service.get_messages(db=db, chat_id=chat_id)