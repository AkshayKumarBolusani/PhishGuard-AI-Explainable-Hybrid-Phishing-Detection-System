import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("MONGODB_USE_MOCK", "true")
os.environ.setdefault("MONGODB_DB_NAME", "phishguard_test")

from app.database.init_db import init_database, shutdown_database
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup isolated MongoDB mock database for tests."""
    init_database()
    yield
    shutdown_database()


@pytest.fixture(autouse=True)
def clean_collections():
    """Clear collections between tests for isolation."""
    from app.database.mongodb import get_database

    db = get_database()
    for name in ("users", "scans", "feedback", "api_keys"):
        db[name].delete_many({})
    yield


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client
