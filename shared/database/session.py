"""
FinCore AI — Database Session Factory
Centralized SQLAlchemy engine and session management.
All microservices import from here to ensure a single source of truth.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL — defaults to SQLite for hackathon, swap to PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fincore.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency — yields a database session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
