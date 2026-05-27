from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ISSPositionOut(BaseModel):
    id: int
    latitude: float
    longitude: float
    altitude: float
    velocity: float
    visibility: str | None
    country: str | None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class SpaceXLaunchOut(BaseModel):
    id: str
    name: str
    date_utc: datetime
    date_precision: str | None
    upcoming: bool
    details: str | None
    webcast_url: str | None
    wikipedia_url: str | None
    patch_small_url: str | None
    provider_name: str | None
    model_config = ConfigDict(from_attributes=True)
