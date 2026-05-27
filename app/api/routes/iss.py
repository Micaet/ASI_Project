import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.models import ISSPositionOut
from app.db.models import ISSPosition
from app.db.session import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/iss", tags=["iss"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/current", response_model=ISSPositionOut)
def get_iss_current(session: SessionDep) -> ISSPosition:
    """Zwraca ostatnią znana pozycję ISS z bazy danych."""
    record = (
        session.query(ISSPosition)
        .order_by(ISSPosition.timestamp.desc())
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Brak danych o pozycji ISS")
    return record


@router.get("/history", response_model=list[ISSPositionOut])
def get_iss_history(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ISSPosition]:
    """Zwraca historię pozycji ISS z paginacją."""
    return (
        session.query(ISSPosition)
        .order_by(ISSPosition.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
