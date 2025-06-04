from fastapi import APIRouter, WebSocket
from ..websockets.chat import chat_ws

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str):
    await chat_ws.handle_connection(websocket, token, user_id)

    # Example of how to handle incoming messages
    async for message in websocket.iter_text():
        data = json.loads(message)
        await handle_message(data, websocket)

async def handle_message(data: dict, websocket: WebSocket):
    message_type = data.get("type")

    if message_type == "message":
        await handle_chat_message(data, websocket)
    elif message_type == "join_chat":
        await handle_join_chat(data, websocket)
    elif message_type == "typing":
        await handle_typing_indicator(data, websocket)

async def handle_chat_message(data: dict, websocket: WebSocket):
    chat_id = data.get("chat_id")
    content = data.get("content")
    message_type = data.get("message_type")

    # Handle the chat message (e.g., broadcast to other participants)
    await chat_ws.broadcast_chat_message(chat_id, content, message_type)

async def handle_join_chat(data: dict, websocket: WebSocket):
    chat_id = data.get("chat_id")

    # Handle joining a chat (e.g., add the user to the chat room)
    await chat_ws.add_user_to_chat(chat_id, websocket)

async def handle_typing_indicator(data: dict, websocket: WebSocket):
    chat_id = data.get("chat_id")
    is_typing = data.get("is_typing")

    # Handle the typing indicator (e.g., broadcast to other participants)
    await chat_ws.broadcast_typing_indicator(chat_id, websocket, is_typing)