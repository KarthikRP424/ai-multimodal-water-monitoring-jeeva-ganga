# conftest.py – pytest fixtures for the JEEVA GANGA backend

import os
import tempfile
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the app after we patch the DATABASE_URL env var

@pytest.fixture(scope="session")
def test_engine():
    # Use an in‑memory SQLite database for tests
    test_url = "sqlite:///:memory:"
    engine = create_engine(test_url, echo=False)
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def db_session(test_engine):
    # Provide a fresh session for each test function
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="session")
def client():
    # Override DATABASE_URL so the app uses the test engine
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    from backend.app.main import app
    client = TestClient(app)
    return client
