# backend/app/database.py

# Import all models so that SQLModel knows about them before creating tables
from . import models  # noqa: F401

from sqlmodel import SQLModel, create_engine, Session
import os

# Database URL – can be overridden via env var (e.g., for testing)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jeeva_ganga.db")

# Use StaticPool for in‑memory SQLite to keep a single connection across sessions
if DATABASE_URL.startswith("sqlite:///:memory:"):
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

def init_db() -> None:
    """Create tables if they do not exist."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    """Return a new SQLModel session bound to the engine."""
    return Session(engine)
