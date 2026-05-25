from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db.models import Base

engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    """Tworzy tabele w bazie jesli jeszcze nie istnieja (CREATE TABLE IF NOT EXISTS)."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Yield sesji z automatycznym zamknięciem."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
