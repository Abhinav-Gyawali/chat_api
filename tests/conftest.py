import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db..db.base import Base
from src.db.session import get_db
from src.main import app
from src.core.security import get_password_hash
from src.models.user import User
from src.models.chat import Chat

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_chat(db_session, test_user):
    chat = Chat(
        name="Test Chat",
        description="Test Description",
        is_group_chat=False,
        created_by=test_user.id
    )
    chat.members.append(test_user.id)
    db_session.add(chat)
    db_session.commit()
    db_session.refresh(chat)
    return chat