from fastapi import WebSocket, Depends, HTTPException
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from ...core.events import ConnectionManager
from ...core.security import get_current_user
from ...models.message import Message
from ...models.chat import Chat
from ...services.chat import ChatService
from ..dependencies import get_db

class ChatWebSocket:
    def __init__(self):
        self.connection_manager = ConnectionManager()
        # Remove the chat_service initialization from __init__
        # We'll create it in handle_connection where we have access to db

    async def handle_chat_message(
        self,
        websocket: WebSocket,
        user_id: int,
        chat_id: int,
        content: str,
        message_type: str,
        db: Session
    ):
        """Handle incoming chat messages"""
        try:
            # Create chat service with db session
            chat_service = ChatService(db)
            
            # Create message in database
            message = await chat_service.send_message(
                db=db,
                chat_id=chat_id,
                message={
                    "content": content,
                    "message_type": message_type,
                    "sender_id": user_id
                }
            )

            # Broadcast to all users in the chat
            await self.connection_manager.broadcast_to_room(
                chat_id,
                {
                    "type": "chat_message",
                    "message": {
                        "id": message.id,
                        "content": content,
                        "message_type": message_type,
                        "sender_id": user_id,
                        "chat_id": chat_id,
                        "created_at": message.created_at.isoformat(),
                    }
                }
            )

            return message

        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": "Failed to process message"
            })
            raise

    async def handle_chat_event(
        self,
        websocket: WebSocket,
        user_id: int,
        event_type: str,
        data: Dict[str, Any],
        db: Session
    ):
        """Handle different types of chat events"""
        # Create chat service with db session
        chat_service = ChatService(db)
        
        if event_type == "join_chat":
            chat_id = data.get("chat_id")
            # Verify user has access to this chat
            chat = await chat_service.get_chat(db, chat_id)
            if not chat or user_id not in [p.id for p in chat.participants]:
                await websocket.send_json({
                    "type": "error",
                    "message": "Access denied to this chat"
                })
                return
                
            await self.connection_manager.join_room(user_id, chat_id)
            await self.connection_manager.broadcast_to_room(
                chat_id,
                {
                    "type": "user_joined",
                    "user_id": user_id,
                    "chat_id": chat_id
                }
            )

        elif event_type == "leave_chat":
            chat_id = data.get("chat_id")
            await self.connection_manager.leave_room(user_id, chat_id)
            await self.connection_manager.broadcast_to_room(
                chat_id,
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "chat_id": chat_id
                }
            )

        elif event_type == "typing":
            chat_id = data.get("chat_id")
            await self.connection_manager.broadcast_to_room(
                chat_id,
                {
                    "type": "typing_indicator",
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "is_typing": data.get("is_typing", True)
                }
            )

    async def handle_connection(self, websocket: WebSocket, token: str, user_id: int, db: Session = Depends(get_db)):
        """Handle WebSocket connection lifecycle"""
        try:
            # Verify token and user
            user = await get_current_user(token)
            if str(user_id) != str(user.id):
                await websocket.close(code=4003)
                return

            await self.connection_manager.connect(websocket, user_id)
            
            try:
                while True:
                    data = await websocket.receive_json()
                    event_type = data.get("type")
                    
                    if event_type == "message":
                        await self.handle_chat_message(
                            websocket,
                            user_id,
                            data["chat_id"],
                            data["content"],
                            data.get("message_type", "text"),
                            db
                        )
                    else:
                        await self.handle_chat_event(
                            websocket,
                            user_id,
                            event_type,
                            data,
                            db
                        )

            except Exception as e:
                await self.connection_manager.disconnect(user_id)
                raise

        except Exception as e:
            await websocket.close(code=4000)
            
        finally:
            await self.connection_manager.disconnect(user_id)

chat_ws = ChatWebSocket()