import mongomock
import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    """
    Replaces real MongoDB client with an in-memory mongomock database for isolated testing.
    """
    mock_client = mongomock.MongoClient(tz_aware=True)
    mock_db = mock_client["test_attendance_db"]

    monkeypatch.setattr(main_module, "client", mock_client)
    monkeypatch.setattr(main_module, "db", mock_db)

    # Initialize indexes
    main_module.init_indexes()
    yield mock_db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
