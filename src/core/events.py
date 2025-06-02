/chat_api/src/core/events.py
from typing import Dict, Set, List
from fastapi import WebSocket
import json
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_rooms: Dict[int, Set[int]] = {}  # user_id: set of chat_ids
        
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
        self.user_rooms.pop(user_id, None)
        
    async def join_room(self, user_id: int, chat_id: int):
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(chat_id)
        
    async def leave_room(self, user_id: int, chat_id: int):
        if user_id in self.user_rooms:
            self.user_rooms[user_id].remove(chat_id)
            
    async def broadcast_to_room(self, chat_id: int, message: dict):
        for user_id, rooms in self.user_rooms.items():
            if chat_id in rooms and user_id in self.active_connections:
                await self.active_connections[user_id].send_json(message)

    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

class CallManager:
    def __init__(self):
        self.active_calls: Dict[int, Dict] = {}  # call_id: call_info
        
    async def start_call(self, call_id: int, caller_id: int, receiver_id: int, call_type: str):
        self.active_calls[call_id] = {
            "caller_id": caller_id,
            "receiver_id": receiver_id,
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