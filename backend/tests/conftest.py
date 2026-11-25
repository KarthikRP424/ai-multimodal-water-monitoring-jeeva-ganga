# conftest.py – pytest fixtures for the JEEVA GANGA backend

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import tempfile
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient

# Import all models so metadata is aware of tables
from backend.app import models  # noqa: F401

@pytest.fixture(scope="session")
def test_engine():
    # Use an in‑memory SQLite database with a StaticPool for shared connections
    test_url = "sqlite:///:memory:"
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        test_url,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    # Provide a fresh session for each test function
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="session")
def client(test_engine):
    # Override DATABASE_URL so the app uses the in‑memory database
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    # Replace the database engine with the test engine before importing the app
    from backend.app import database as db_mod
    db_mod.engine = test_engine
    # Ensure tables are created on the test engine
    db_mod.init_db()
    # Import the FastAPI app (startup event will use the overridden engine)
    from backend.app.main import app
    client = TestClient(app)
    return client