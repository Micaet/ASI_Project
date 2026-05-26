from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://space:space@localhost:5432/space_monitor"

    iss_poll_seconds: int = 30
    spacex_poll_seconds: int = 3600

    nominatim_user_agent: str = "SpaceMonitor/1.0 kontakt@example.com"

    log_level: str = "INFO"

    model_config = {"env_prefix": "APP_"}


settings = Settings()
