from typing import Dict, Set, List
from fastapi import WebSocket
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, Set[int]] = {}
        
    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket
        
    async def disconnect(self, username: str):
        """Safely handle disconnection"""
        if username in self.active_connections:
            websocket = self.active_connections.pop(username)
            try:
                await websocket.close()
            except Exception:
                pass
        self.user_rooms.pop(username, None)
        
    async def join_room(self, username: str, chat_id: int):
        if username not in self.user_rooms:
            self.user_rooms[username] = set()
        self.user_rooms[username].add(chat_id)
        
    async def leave_room(self, username: str, chat_id: int):
        if username in self.user_rooms:
            self.user_rooms[username].remove(chat_id)
            
    async def broadcast_to_room(self, chat_id: int, message: dict):
        for username, rooms in self.user_rooms.items():
            if chat_id in rooms and username in self.active_connections:
                await self.active_connections[username].send_json(message)

    async def send_personal_message(self, username: str, message: dict):
        if username in self.active_connections:
            await self.active_connections[username].send_json(message)

class CallManager:
    def __init__(self):
        self.active_calls: Dict[int, Dict] = {}  # call_id: call_info
        
    async def start_call(self, call_id: int, caller_user: int, receiver_user: int, call_type: str):
        self.active_calls[call_id] = {
            "caller_user": caller_user,
            "receiver_user": receiver_user,
            "type": call_type,
            "start_time": datetime.utcnow(),
            "status": "ringing"
        }
        
    async def end_call(self, call_id: int):
        if call_id in self.active_calls:
            call_info = self.active_calls.pop(call_id)
            duration = (datetime.utcnow() - call_info["start_time"]).seconds
            return duration
        return None

    async def update_call_status(self, call_id: int, status: str):
        if call_id in self.active_calls:
            self.active_calls[call_id]["status"] = status