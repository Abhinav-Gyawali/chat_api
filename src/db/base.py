from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
from ..core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.DB_ECHO_LOG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def get_db() -> Generator:
    """
    Generator function to get database session.
    Yields a SQLAlchemy session and handles closing it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()