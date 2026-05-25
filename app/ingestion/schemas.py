from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ISSPositionResponse(BaseModel):
    """Schemat odpowiedzi z WhereTheISS.at API."""

    latitude: float
    longitude: float
    altitude: float
    velocity: float
    visibility: str
    timestamp: int

    @field_validator("latitude")
    @classmethod
    def lat_in_range(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude {v} spoza zakresu [-90, 90]")
        return v

    @field_validator("longitude")
    @classmethod
    def lon_in_range(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError(f"Longitude {v} spoza zakresu [-180, 180]")
        return v


class OpenNotifyPosition(BaseModel):
    """Pozycja z Open Notify API."""

    latitude: float
    longitude: float


class OpenNotifyResponse(BaseModel):
    """Schemat odpowiedzi z Open Notify API (fallback dla ISS)."""

    iss_position: OpenNotifyPosition
    timestamp: int

    def to_iss_position_response(self) -> ISSPositionResponse:
        """Konwertuje odpowiedz Open Notify do wspolnego formatu z zerami dla brakujacych pol."""
        return ISSPositionResponse(
            latitude=self.iss_position.latitude,
            longitude=self.iss_position.longitude,
            altitude=0.0,
            velocity=0.0,
            visibility="unknown",
            timestamp=self.timestamp,
        )


class RLLProvider(BaseModel):
    """Dostawca startu z RocketLaunch.Live API."""

    name: str | None = None


class RLLVehicle(BaseModel):
    """Pojazd startowy z RocketLaunch.Live API."""

    name: str | None = None


class RLLMission(BaseModel):
    """Misja z RocketLaunch.Live API."""

    name: str | None = None
    description: str | None = None


class RLLLaunchResponse(BaseModel):
    """Schemat pojedynczego startu z RocketLaunch.Live API."""

    id: int
    name: str
    t0: str | None = None
    sort_date: str
    provider: RLLProvider | None = None
    vehicle: RLLVehicle | None = None
    missions: list[RLLMission] = Field(default_factory=list)
    launch_description: str | None = None


class RLLResponse(BaseModel):
    """Odpowiedz z RocketLaunch.Live API."""

    count: int
    result: list[RLLLaunchResponse] = Field(default_factory=list)


class NominatimResponse(BaseModel):
    """Schemat odpowiedzi z Nominatim reverse geocoding."""

    address: dict = Field(default_factory=dict)

    @property
    def country(self) -> str | None:
        return self.address.get("country")
