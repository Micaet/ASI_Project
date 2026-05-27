from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.db.session import get_session


def override_session_empty():
    """Mock sesji ktory udaje pusta baze."""
    session = MagicMock()
    session.query.return_value.order_by.return_value.first.return_value = None
    session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
    session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    yield session


@pytest.fixture
def client_empty_db():
    app.dependency_overrides[get_session] = override_session_empty
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health(client_empty_db):
    """Health check zawsze zwraca 200 OK."""
    resp = client_empty_db.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_iss_current_no_data(client_empty_db):
    """Brak danych ISS w bazie -- endpoint zwraca 404."""
    resp = client_empty_db.get("/iss/current")
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_iss_history_empty(client_empty_db):
    """Pusta historia ISS -- zwraca pusta liste, nie blad."""
    resp = client_empty_db.get("/iss/history")
    assert resp.status_code == 200
    assert resp.json() == []


def test_iss_history_limit_validation(client_empty_db):
    """Limit 0 jest nieprawidlowy (minimum 1) -- 422."""
    resp = client_empty_db.get("/iss/history?limit=0")
    assert resp.status_code == 422


def test_iss_history_limit_too_large(client_empty_db):
    """Limit 9999 przekracza maksimum (1000) -- 422."""
    resp = client_empty_db.get("/iss/history?limit=9999")
    assert resp.status_code == 422


def test_iss_history_negative_offset(client_empty_db):
    """Ujemny offset jest nieprawidlowy -- 422."""
    resp = client_empty_db.get("/iss/history?offset=-1")
    assert resp.status_code == 422


def test_launches_upcoming_empty(client_empty_db):
    """Brak nadchodzacych startow -- pusta lista."""
    resp = client_empty_db.get("/launches/upcoming")
    assert resp.status_code == 200
    assert resp.json() == []


def test_launches_past_empty(client_empty_db):
    """Brak historycznych startow -- pusta lista."""
    resp = client_empty_db.get("/launches/past")
    assert resp.status_code == 200
    assert resp.json() == []


def test_launches_past_limit_validation(client_empty_db):
    """Limit 0 jest nieprawidlowy (minimum 1) -- 422."""
    resp = client_empty_db.get("/launches/past?limit=0")
    assert resp.status_code == 422


def test_launches_past_limit_too_large(client_empty_db):
    """Limit 999 przekracza maksimum (200) -- 422."""
    resp = client_empty_db.get("/launches/past?limit=999")
    assert resp.status_code == 422
