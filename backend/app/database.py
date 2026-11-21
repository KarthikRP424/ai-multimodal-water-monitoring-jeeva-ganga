# backend/app/database.py

from sqlmodel import SQLModel, create_engine, Session
import os

# Database URL – can be overridden via env var (e.g., for testing)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jeeva_ganga.db")
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    """Create tables if they do not exist."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    """Return a new SQLModel session bound to the engine."""
    return Session(engine)
