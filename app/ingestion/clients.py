import logging

import httpx

from app.config import settings
from app.ingestion.schemas import (
    ISSPositionResponse,
    NominatimResponse,
    OpenNotifyResponse,
    RLLLaunchResponse,
    RLLResponse,
)

logger = logging.getLogger(__name__)

ISS_URL = "https://api.wheretheiss.at/v1/satellites/25544"
ISS_FALLBACK_URL = "http://api.open-notify.org/iss-now.json"
RLL_URL = "https://fdo.rocketlaunch.live/json/launches/next/5"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

TIMEOUT = httpx.Timeout(20.0, connect=12.0)


async def fetch_iss_position() -> ISSPositionResponse | None:
    """Pobiera aktualną pozycję ISS; przy błędzie próbuje fallback Open Notify."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            resp = await client.get(ISS_URL)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("ISS raw response: %s", data)
            return ISSPositionResponse.model_validate(data)
        except Exception as e:
            logger.warning("WhereTheISS.at niedostępne (%s), próbuję Open Notify...", e)

        try:
            resp = await client.get(ISS_FALLBACK_URL)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("Open Notify raw response: %s", data)
            return OpenNotifyResponse.model_validate(data).to_iss_position_response()
        except Exception as e:
            logger.error("Fallback Open Notify również zawiódł: %s", e)
            return None


async def fetch_rll_launches() -> list[RLLLaunchResponse]:
    """Pobiera najbliższe starty z RocketLaunch.Live API."""
    try:
        # verify=False -- siec uczelniana robi TLS inspection z self-signed cert
        async with httpx.AsyncClient(timeout=TIMEOUT, verify=False) as client:
            resp = await client.get(RLL_URL)
            resp.raise_for_status()
            parsed = RLLResponse.model_validate(resp.json())
            logger.info("RLL: pobrano %d startów", len(parsed.result))
            return parsed.result
    except httpx.HTTPStatusError as e:
        logger.error("Błąd HTTP RLL (%s): %s", e.response.status_code, e)
    except httpx.HTTPError as e:
        logger.error("Błąd sieci RLL: %s", e)
    except Exception as e:
        logger.error("Nieoczekiwany błąd RLL: %s", e)
    return []


async def reverse_geocode(lat: float, lon: float) -> str | None:
    """Zwraca nazwę kraju dla danych współrzędnych (Nominatim)."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(
                NOMINATIM_URL,
                params={"lat": lat, "lon": lon, "format": "json", "zoom": 3},
                headers={"User-Agent": settings.nominatim_user_agent},
            )
            resp.raise_for_status()
            data = resp.json()

            if "error" in data:
                logger.debug("Nominatim: brak wyniku (ocean?) lat=%.2f lon=%.2f", lat, lon)
                return None

            result = NominatimResponse.model_validate(data)
            return result.country

    except httpx.HTTPError as e:
        logger.warning("Błąd Nominatim: %s", e)
        return None
    except Exception as e:
        logger.warning("Nieoczekiwany błąd Nominatim: %s", e)
        return None
