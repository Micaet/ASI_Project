import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import iss, launches

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Space Activity Monitor API",
    description="API do monitorowania pozycji ISS i startów SpaceX",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(iss.router)
app.include_router(launches.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Zwraca status serwisu."""
    return {"status": "ok"}
