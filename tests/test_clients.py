from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.clients import fetch_iss_position, fetch_rll_launches, reverse_geocode


@pytest.mark.asyncio
async def test_fetch_iss_position_success():
    """Poprawna odpowiedz z WhereTheISS.at."""
    fake_response = MagicMock()
    fake_response.json.return_value = {
        "latitude": 51.5,
        "longitude": -0.1,
        "altitude": 408.0,
        "velocity": 27600.0,
        "visibility": "daylight",
        "timestamp": 1700000000,
    }
    fake_response.raise_for_status = MagicMock()

    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=fake_response
        )
        result = await fetch_iss_position()

    assert result is not None
    assert result.latitude == 51.5
    assert result.altitude == 408.0


@pytest.mark.asyncio
async def test_fetch_iss_position_fallback():
    """WhereTheISS pada -- powinien uzyc Open Notify."""
    fail_response = MagicMock()
    fail_response.raise_for_status.side_effect = Exception("timeout")

    fallback_response = MagicMock()
    fallback_response.json.return_value = {
        "iss_position": {"latitude": 10.0, "longitude": 20.0},
        "timestamp": 1700000000,
    }
    fallback_response.raise_for_status = MagicMock()

    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=[fail_response, fallback_response]
        )
        result = await fetch_iss_position()

    assert result is not None
    assert result.latitude == 10.0
    assert result.altitude == 0.0


@pytest.mark.asyncio
async def test_fetch_iss_position_both_fail():
    """Oba API padaja -- zwraca None."""
    fail_response = MagicMock()
    fail_response.raise_for_status.side_effect = Exception("timeout")

    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=fail_response
        )
        result = await fetch_iss_position()

    assert result is None


@pytest.mark.asyncio
async def test_fetch_rll_launches_success():
    """Poprawna odpowiedz z RocketLaunch.Live."""
    fake_response = MagicMock()
    fake_response.json.return_value = {
        "count": 1,
        "result": [
            {
                "id": 5985,
                "name": "Starlink",
                "t0": "2026-05-24T14:00Z",
                "sort_date": "1779631200",
                "provider": {"name": "SpaceX"},
                "vehicle": {"name": "Falcon 9"},
                "missions": [],
                "launch_description": "Test launch",
            }
        ],
    }
    fake_response.raise_for_status = MagicMock()

    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=fake_response
        )
        result = await fetch_rll_launches()

    assert len(result) == 1
    assert result[0].name == "Starlink"


@pytest.mark.asyncio
async def test_fetch_rll_launches_error():
    """Blad sieci RLL -- zwraca pusta liste."""
    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("connection refused")
        )
        result = await fetch_rll_launches()

    assert result == []


@pytest.mark.asyncio
async def test_reverse_geocode_success():
    """Nominatim zwraca kraj."""
    fake_response = MagicMock()
    fake_response.json.return_value = {
        "address": {"country": "Poland", "country_code": "pl"}
    }
    fake_response.raise_for_status = MagicMock()

    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=fake_response
        )
        result = await reverse_geocode(52.23, 21.01)

    assert result == "Poland"


@pytest.mark.asyncio
async def test_reverse_geocode_ocean():
    """Punkt na oceanie -- Nominatim zwraca error."""
    fake_response = MagicMock()
    fake_response.json.return_value = {"error": "Unable to geocode"}
    fake_response.raise_for_status = MagicMock()

    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=fake_response
        )
        result = await reverse_geocode(0.0, 0.0)

    assert result is None


@pytest.mark.asyncio
async def test_reverse_geocode_network_error():
    """Blad sieci Nominatim -- zwraca None, nie rzuca wyjatku."""
    with patch("app.ingestion.clients.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=Exception("timeout")
        )
        result = await reverse_geocode(52.23, 21.01)

    assert result is None
