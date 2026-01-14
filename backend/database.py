"""Database configuration and session management for SQLite3 using SQLAlchemy"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic_settings import BaseSettings
from typing import Generator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./savefood.db"
    )
    jwt_secret: str = os.getenv("JWT_SECRET", "save-food-secret-key-2024")
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", 5000))

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()

# SQLAlchemy setup
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all tables (for testing/cleanup)"""
    Base.metadata.drop_all(bind=engine)
