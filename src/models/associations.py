from sqlalchemy import Column, Integer, ForeignKey, Table, String
from ..db.base import Base

chat_users = Table(
    'chat_users',
    Base.metadata,
    Column('username', String, ForeignKey('users.username'), primary_key=True),
    Column('chat_id', Integer, ForeignKey('chats.id'), primary_key=True)
)