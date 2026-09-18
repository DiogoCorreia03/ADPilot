from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    ad_state_dir: Path = Field(
        default=Path("./ad-pentest/state"),
        alias="AD_STATE_DIR",
    )
    agent_phase_header: str = Field(
        default="pentest_phase",
        description="HTTP header key passed by client indicating current pentest phase",
    )

    @property
    def credentials_file(self) -> Path:
        return self.ad_state_dir / "credentials.json"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    try:
        return Settings()
    except Exception as e:
        print(f"Error occurred while initializing settings: {e}")
        raise
