import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.models import SpaceXLaunchOut
from app.db.models import SpaceXLaunch
from app.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/launches", tags=["launches"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/upcoming", response_model=list[SpaceXLaunchOut])
def get_launches_upcoming(session: SessionDep) -> list[SpaceXLaunch]:
    """Zwraca starty SpaceX oznaczone jako nadchodzące, posortowane rosnąco po dacie."""
    return (
        session.query(SpaceXLaunch)
        .filter(SpaceXLaunch.upcoming.is_(True))
        .order_by(SpaceXLaunch.date_utc.asc())
        .all()
    )


@router.get("/past", response_model=list[SpaceXLaunchOut])
def get_launches_past(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
) -> list[SpaceXLaunch]:
    """Zwraca ostatnie historyczne starty SpaceX posortowane malejąco po dacie."""
    return (
        session.query(SpaceXLaunch)
        .filter(SpaceXLaunch.upcoming.is_(False))
        .order_by(SpaceXLaunch.date_utc.desc())
        .limit(limit)
        .all()
    )
