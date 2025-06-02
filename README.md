# fastapi-chat

This is a real-time chat application built with FastAPI, featuring WebSocket support, user authentication, and a modular project structure.

## Features

- **User Authentication**: Secure signup, login, and token refresh functionalities.
- **Chat System**: Create and manage chats, send and fetch messages.
- **Real-Time Messaging**: WebSocket connections for instant message delivery.
- **User Presence Tracking**: Monitor user online/offline status.

## Project Structure

```
fastapi-chat
├── src
│   ├── api
│   │   ├── dependencies.py
│   │   ├── endpoints
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   └── users.py
│   │   └── websockets
│   │       └── chat.py
│   ├── core
│   │   ├── config.py
│   │   ├── security.py
│   │   └── events.py
│   ├── db
│   │   ├── base.py
│   │   └── session.py
│   ├── models
│   │   ├── chat.py
│   │   ├── message.py
│   │   └── user.py
│   ├── schemas
│   │   ├── chat.py
│   │   ├── message.py
│   │   └── user.py
│   ├── services
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── user.py
│   └── main.py
├── tests
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_chat.py
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-chat.git
   cd fastapi-chat
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

## Usage

- **Authentication**: Use the `/auth` endpoints to register and log in users.
- **Chat**: Access the `/chat` endpoints to create and manage chats.
- **WebSocket**: Connect to the WebSocket endpoint for real-time messaging.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.