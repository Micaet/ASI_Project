import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.models import ISSPosition, SpaceXLaunch
from app.db.session import SessionLocal
from app.ingestion.clients import (
    fetch_iss_position,
    fetch_rll_launches,
    reverse_geocode,
)
from app.ingestion.schemas import RLLLaunchResponse

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Uruchamia coroutine w nowej pętli (APScheduler wywołuje joby synchronicznie)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def ingest_iss() -> None:
    """Job: pobiera pozycję ISS, robi reverse geocoding, zapisuje do bazy."""
    _run_async(_ingest_iss_async())


async def _ingest_iss_async() -> None:
    pos = await fetch_iss_position()
    if pos is None:
        return

    country = await reverse_geocode(pos.latitude, pos.longitude)
    ts = datetime.fromtimestamp(pos.timestamp, tz=timezone.utc)

    session = SessionLocal()
    try:
        exists = (
            session.query(ISSPosition.id)
            .filter(ISSPosition.timestamp == ts)
            .first()
        )
        if exists:
            logger.debug("ISS pozycja z ts=%s już istnieje, pomijam", ts)
            return

        record = ISSPosition(
            latitude=pos.latitude,
            longitude=pos.longitude,
            altitude=pos.altitude,
            velocity=pos.velocity,
            visibility=pos.visibility,
            country=country,
            timestamp=ts,
            fetched_at=datetime.now(timezone.utc),
        )
        session.add(record)
        session.commit()
        logger.info(
            "ISS: lat=%.2f lon=%.2f alt=%.1f km, kraj=%s",
            pos.latitude,
            pos.longitude,
            pos.altitude,
            country or "ocean/brak",
        )
    except Exception as e:
        session.rollback()
        logger.error("Błąd zapisu ISS: %s", e)
    finally:
        session.close()


def ingest_launches() -> None:
    """Job: pobiera starty z RocketLaunch.Live, upsertuje do bazy."""
    _run_async(_ingest_launches_async())


ingest_spacex = ingest_launches


async def _ingest_launches_async() -> None:
    launches = await fetch_rll_launches()
    if not launches:
        return

    now = datetime.now(timezone.utc)
    session = SessionLocal()
    try:
        for launch in launches:
            values = _build_launch_values(launch, now)
            stmt = pg_insert(SpaceXLaunch).values(**values)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={k: stmt.excluded[k] for k in values if k != "id"},
            )
            session.execute(stmt)

        session.commit()
        logger.info("RLL: upsertowano %d startów", len(launches))
    except Exception as e:
        session.rollback()
        logger.error("Błąd zapisu RLL: %s", e)
    finally:
        session.close()


def _build_launch_values(launch: RLLLaunchResponse, now: datetime) -> dict:
    """Mapuje pola RocketLaunch.Live na kolumny tabeli SpaceXLaunch."""
    if launch.t0:
        date_utc = datetime.fromisoformat(launch.t0.replace("Z", "+00:00"))
        date_precision = "minute"
    else:
        date_utc = datetime.fromtimestamp(int(launch.sort_date), tz=timezone.utc)
        date_precision = "day"

    details = launch.launch_description
    if not details and launch.missions:
        details = launch.missions[0].description

    return {
        "id": str(launch.id),
        "name": launch.name,
        "rocket_id": launch.vehicle.name if launch.vehicle else None,
        "date_utc": date_utc,
        "date_precision": date_precision,
        "upcoming": True,
        "details": details,
        "webcast_url": None,
        "wikipedia_url": None,
        "patch_small_url": None,
        "provider_name": launch.provider.name if launch.provider else None,
        "updated_at": now,
    }
