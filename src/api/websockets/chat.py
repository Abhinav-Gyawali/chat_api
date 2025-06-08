from fastapi import WebSocket, Depends, HTTPException
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from ...core.events import ConnectionManager
from ...core.security import get_current_user
from ...models.message import Message
from ...services.chat import ChatService

class ChatWebSocket:
    def __init__(self):
        self.connection_manager = ConnectionManager()

    async def handle_connection(self, websocket: WebSocket, token: str, username: str):
        """Handle WebSocket connection lifecycle"""
        try:
            # Verify token and user
            user = await get_current_user(token)
            if username != user.username:
                await websocket.close(code=4003)
                return

            # Send initial connection success message
            await websocket.send_json({
                "type": "connection_established",
                "username": username
            })

        except Exception as e:
            print(f"Connection error: {str(e)}")
            try:
                await websocket.close(code=4000)
            except RuntimeError:
                # Connection already closed
                pass
            raise

    async def handle_message(self, data: dict, websocket: WebSocket, username: str):
        """Handle real-time messages"""
        message_type = data.get("type")
        
        handlers = {
            # Real-time features only
            "new_message": self.handle_new_message,
            "typing": self.handle_typing_indicator,
            "presence": self.handle_presence_update,
            "read_receipt": self.handle_read_receipt
        }

        handler = handlers.get(message_type)
        if handler:
            await handler(data, username)
        else:
            await websocket.send_json({
                "type": "error",
                "message": "Unknown message type"
            })

    async def handle_new_message(self, data: dict, username: str):
        """Handle new chat message"""
        try:
            chat_id = data["chat_id"]
            content = data["content"]
            
            # Broadcast message to all users in the chat room
            await self.connection_manager.broadcast_to_room(chat_id, {
                "type": "new_message",
                "message": {
                    "content": content,
                    "sender": username,
                    "chat_id": chat_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })
        except Exception as e:
            print(f"Error broadcasting message: {str(e)}")

    async def handle_typing_indicator(self, data: dict, username: str):
        """Handle typing status"""
        chat_id = data["chat_id"]
        is_typing = data["is_typing"]
        
        await self.connection_manager.broadcast_to_chat(chat_id, {
            "type": "typing",
            "username": username,
            "chat_id": chat_id,
            "is_typing": is_typing
        }, exclude_user=username)

    async def handle_presence_update(self, data: dict, username: str):
        """Handle online/offline status"""
        status = data["status"]
        await self.connection_manager.broadcast_presence({
            "type": "presence",
            "username": username,
            "status": status
        })

    async def handle_read_receipt(self, data: dict, username: str):
        """Handle message read receipts"""
        chat_id = data["chat_id"]
        message_id = data["message_id"]
        
        await self.connection_manager.broadcast_to_chat(chat_id, {
            "type": "read_receipt",
            "username": username,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def leave_room(self, username: str, chat_id: int):
        """Remove a user from a chat room"""
        if username in self.connection_manager.user_rooms:
            self.connection_manager.user_rooms[username].remove(chat_id)

chat_ws = ChatWebSocket()