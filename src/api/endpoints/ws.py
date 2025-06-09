from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, HTTPException
from ..websockets.chat import chat_ws
from ...schemas.message import MessageCreate, MessageType
from ..dependencies import get_db, get_current_user
import json
from datetime import datetime

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/chat")  # Remove {chat_id} parameter
async def websocket_endpoint(
    websocket: WebSocket
):
    """
    Single WebSocket endpoint for handling all chats
    """
    try:
        # Get token from query parameters
        access_token = websocket.query_params.get("token")
        if not access_token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return

        if access_token.startswith('Bearer '):
            access_token = access_token.replace('Bearer ', '')

        # Get database session
        db = next(get_db())

        try:
            # Authenticate user
            user = await get_current_user(db=db, token=access_token)
            if not user:
                await websocket.close(code=4003, reason="Authentication failed")
                return
            
            username = user.username
            print(f"User authenticated: {username}")

            # Accept connection
            await websocket.accept()

            # Set up WebSocket connection
            await chat_ws.handle_connection(websocket, access_token, username)

            # Send connection confirmation
            await websocket.send_json({
                "type": "connected",
                "username": username,
                "status": "connected"
            })

            # Handle incoming messages
            while True:
                try:
                    raw_message = await websocket.receive_text()
                    data = json.loads(raw_message)
                    
                    # Each message must include chat_id
                    if "chat_id" not in data:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Missing chat_id in message"
                        })
                        continue

                    # Join chat room if not already joined
                    chat_id = data["chat_id"]
                    await chat_ws.connection_manager.join_room(username, chat_id)
                    
                    print(f"Received message from {username} in chat {chat_id}: {data}")
                    await chat_ws.handle_message(data, websocket, username)
                    
                except WebSocketDisconnect:
                    print(f"Client disconnected normally: {username}")
                    break
                except json.JSONDecodeError:
                    print(f"Invalid JSON received from {username}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format"
                    })
                except Exception as e:
                    print(f"Message handling error: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to process message"
                    })

        except HTTPException as http_exc:
            print(f"HTTP error: {str(http_exc.detail)}")
            await websocket.close(code=http_exc.status_code, reason=str(http_exc.detail))
            return

    except WebSocketDisconnect:
        print(f"Client disconnected: {username if 'username' in locals() else 'Unknown'}")
    except Exception as e:
        print(f"Connection error: {str(e)}")
        await websocket.close(code=1011, reason=str(e))
    finally:
        if 'username' in locals():
            try:
                # Disconnect from all rooms
                await chat_ws.connection_manager.disconnect(username)
            except Exception as e:
                print(f"Cleanup error: {str(e)}")

async def handle_message(data: dict, websocket: WebSocket, username: str):
    """Handle real-time WebSocket messages"""
    message_type = data.get("type")
    
    handlers = {
        # Real-time features only
        "new_message": handle_chat_message,
        "typing": handle_typing_indicator,
        "presence": handle_user_presence,
        "read_receipt": handle_mark_as_read
    }

    handler = handlers.get(message_type)
    if handler:
        await handler(data, websocket, username)
    else:
        await websocket.send_json({
            "type": "error",
            "message": "Unknown message type"
        })

async def handle_chat_message(data: dict, websocket: WebSocket, username: str):
    """Handle sending chat messages"""
    try:
        message = MessageCreate(
            chat_id=data["chat_id"],
            content=data["content"],
            message_type=MessageType(data.get("message_type", "text")),
            media_url=data.get("media_url")
        )
        
        # Send message through WebSocket
        await chat_ws.broadcast_to_chat(data["chat_id"], {
            "type": "new_message",
            "message": {
                "content": message.content,
                "sender": username,
                "chat_id": message.chat_id,
                "message_type": message.message_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        # Send delivery receipt
        await websocket.send_json({
            "type": "message_sent",
            "chat_id": message.chat_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

async def handle_typing_indicator(data: dict, websocket: WebSocket, username: str):
    """Handle typing indicators"""
    chat_id = data["chat_id"]
    is_typing = data["is_typing"]
    
    await chat_ws.broadcast_to_chat(chat_id, {
        "type": "typing_indicator",
        "username": username,
        "chat_id": chat_id,
        "is_typing": is_typing
    }, exclude_user=username)

async def handle_user_presence(data: dict, websocket: WebSocket, username: str):
    """Handle online/offline status"""
    status = data["status"]
    await chat_ws.broadcast_presence({
        "type": "presence",
        "username": username,
        "status": status
    })

async def handle_mark_as_read(data: dict, websocket: WebSocket, username: str):
    """Handle real-time read receipts"""
    try:
        chat_id = data["chat_id"]
        message_id = data["message_id"]
        
        await chat_ws.broadcast_to_chat(chat_id, {
            "type": "read_receipt",
            "username": username,
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })