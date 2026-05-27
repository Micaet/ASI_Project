import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_session():
    return MagicMock()
