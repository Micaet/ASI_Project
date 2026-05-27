from datetime import datetime, timezone

from app.ingestion.schemas import RLLLaunchResponse
from app.ingestion.service import _build_launch_values


NOW = datetime(2026, 5, 25, tzinfo=timezone.utc)


def test_build_launch_values_with_t0():
    """Start z konkretna data t0 -- precyzja 'minute'."""
    launch = RLLLaunchResponse.model_validate({
        "id": 100,
        "name": "Falcon 9",
        "t0": "2026-06-01T10:00Z",
        "sort_date": "1780000000",
        "provider": {"name": "SpaceX"},
        "vehicle": {"name": "Falcon 9"},
    })

    result = _build_launch_values(launch, NOW)

    assert result["id"] == "100"
    assert result["name"] == "Falcon 9"
    assert result["date_precision"] == "minute"
    assert result["provider_name"] == "SpaceX"
    assert result["rocket_id"] == "Falcon 9"
    assert result["upcoming"] is True


def test_build_launch_values_without_t0():
    """Start bez t0 -- uzywa sort_date, precyzja 'day'."""
    launch = RLLLaunchResponse.model_validate({
        "id": 200,
        "name": "Unknown Launch",
        "t0": None,
        "sort_date": "1800000000",
    })

    result = _build_launch_values(launch, NOW)

    assert result["date_precision"] == "day"
    assert result["provider_name"] is None
    assert result["rocket_id"] is None
    assert result["webcast_url"] is None
    assert result["wikipedia_url"] is None


def test_build_launch_values_details_from_mission():
    """Brak launch_description -- bierze opis z pierwszej misji."""
    launch = RLLLaunchResponse.model_validate({
        "id": 300,
        "name": "Test Launch",
        "t0": "2026-07-01T12:00Z",
        "sort_date": "1800000000",
        "launch_description": None,
        "missions": [{"name": "M1", "description": "Opis misji testowej"}],
    })

    result = _build_launch_values(launch, NOW)

    assert result["details"] == "Opis misji testowej"


def test_build_launch_values_details_from_launch_description():
    """Jest launch_description -- uzywa go zamiast misji."""
    launch = RLLLaunchResponse.model_validate({
        "id": 400,
        "name": "Test Launch 2",
        "t0": "2026-07-01T12:00Z",
        "sort_date": "1800000000",
        "launch_description": "Opis ze startu",
        "missions": [{"name": "M1", "description": "Opis z misji"}],
    })

    result = _build_launch_values(launch, NOW)

    assert result["details"] == "Opis ze startu"


def test_build_launch_values_no_details():
    """Brak opisu i brak misji -- details to None."""
    launch = RLLLaunchResponse.model_validate({
        "id": 500,
        "name": "Mysterious Launch",
        "t0": None,
        "sort_date": "1800000000",
        "launch_description": None,
        "missions": [],
    })

    result = _build_launch_values(launch, NOW)

    assert result["details"] is None


def test_build_launch_values_updated_at():
    """updated_at powinien byc ustawiony na przekazany czas 'now'."""
    launch = RLLLaunchResponse.model_validate({
        "id": 600,
        "name": "Timestamp Test",
        "t0": "2026-08-01T00:00Z",
        "sort_date": "1800000000",
    })

    result = _build_launch_values(launch, NOW)

    assert result["updated_at"] == NOW
