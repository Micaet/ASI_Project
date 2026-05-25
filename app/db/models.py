from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ISSPosition(Base):
    __tablename__ = "iss_positions"

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    velocity = Column(Float, nullable=False)
    visibility = Column(String(32))
    country = Column(String(128))
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    fetched_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return (
            f"<ISSPosition lat={self.latitude:.2f} "
            f"lon={self.longitude:.2f} "
            f"country={self.country}>"
        )


class SpaceXLaunch(Base):
    __tablename__ = "spacex_launches"

    id = Column(String(64), primary_key=True)
    name = Column(String(256), nullable=False)
    rocket_id = Column(String(64))
    date_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    date_precision = Column(String(16))
    upcoming = Column(Boolean, nullable=False)
    details = Column(Text)
    webcast_url = Column(String(512))
    wikipedia_url = Column(String(512))
    patch_small_url = Column(String(512))
    provider_name = Column(String(128))
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<SpaceXLaunch name={self.name!r} date={self.date_utc}>"
