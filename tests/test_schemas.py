import pytest

from pydantic import ValidationError

from app.ingestion.schemas import (
    ISSPositionResponse,
    NominatimResponse,
    OpenNotifyResponse,
    RLLLaunchResponse,
    RLLResponse,
)


def test_iss_response_valid():
    """Poprawne dane ISS -- model tworzy sie bez bledu."""
    data = {
        "latitude": 51.5,
        "longitude": -0.1,
        "altitude": 408.0,
        "velocity": 27600.0,
        "visibility": "daylight",
        "timestamp": 1700000000,
    }
    result = ISSPositionResponse.model_validate(data)
    assert result.latitude == 51.5
    assert result.altitude == 408.0


def test_iss_response_invalid_lat():
    """Latitude 95 spoza zakresu [-90, 90] -- ValidationError."""
    data = {
        "latitude": 95.0,
        "longitude": 0.0,
        "altitude": 408.0,
        "velocity": 27600.0,
        "visibility": "daylight",
        "timestamp": 1700000000,
    }
    with pytest.raises(ValidationError):
        ISSPositionResponse.model_validate(data)


def test_iss_response_invalid_lon():
    """Longitude -200 spoza zakresu [-180, 180] -- ValidationError."""
    data = {
        "latitude": 0.0,
        "longitude": -200.0,
        "altitude": 408.0,
        "velocity": 27600.0,
        "visibility": "daylight",
        "timestamp": 1700000000,
    }
    with pytest.raises(ValidationError):
        ISSPositionResponse.model_validate(data)


def test_open_notify_to_iss_response():
    """Konwersja Open Notify do wspolnego formatu -- altitude i velocity to 0."""
    data = {
        "iss_position": {"latitude": 10.0, "longitude": 20.0},
        "timestamp": 1700000000,
    }
    result = OpenNotifyResponse.model_validate(data).to_iss_position_response()
    assert result.latitude == 10.0
    assert result.longitude == 20.0
    assert result.altitude == 0.0
    assert result.velocity == 0.0
    assert result.visibility == "unknown"


def test_rll_launch_valid():
    """Poprawne dane startu z RocketLaunch.Live."""
    data = {
        "id": 5985,
        "name": "Starlink (17-37)",
        "t0": "2026-05-24T14:00Z",
        "sort_date": "1779631200",
        "provider": {"name": "SpaceX"},
        "vehicle": {"name": "Falcon 9"},
        "missions": [{"name": "Starlink (17-37)", "description": None}],
        "launch_description": "A SpaceX Falcon 9 rocket will launch Starlink.",
    }
    result = RLLLaunchResponse.model_validate(data)
    assert result.id == 5985
    assert result.name == "Starlink (17-37)"
    assert result.t0 == "2026-05-24T14:00Z"
    assert result.provider is not None
    assert result.provider.name == "SpaceX"
    assert result.vehicle is not None
    assert result.vehicle.name == "Falcon 9"


def test_rll_launch_no_t0():
    """Start bez ustalonej daty -- t0 moze byc None."""
    data = {
        "id": 9999,
        "name": "Unknown Launch",
        "t0": None,
        "sort_date": "1800000000",
    }
    result = RLLLaunchResponse.model_validate(data)
    assert result.t0 is None
    assert result.sort_date == "1800000000"
    assert result.provider is None
    assert result.missions == []


def test_rll_response_pagination():
    """RLLResponse parsuje liste startow z polem count."""
    data = {
        "count": 2,
        "result": [
            {"id": 1, "name": "Launch A", "t0": "2026-06-01T10:00Z", "sort_date": "1780000000"},
            {"id": 2, "name": "Launch B", "t0": None, "sort_date": "1785000000"},
        ],
    }
    result = RLLResponse.model_validate(data)
    assert result.count == 2
    assert len(result.result) == 2
    assert result.result[0].name == "Launch A"


def test_nominatim_response_country():
    """Nominatim zwraca kraj w adresie."""
    data = {"address": {"country": "Poland", "country_code": "pl"}}
    result = NominatimResponse.model_validate(data)
    assert result.country == "Poland"


def test_nominatim_response_country_missing():
    """Pusty adres -- country to None."""
    data = {"address": {}}
    result = NominatimResponse.model_validate(data)
    assert result.country is None
