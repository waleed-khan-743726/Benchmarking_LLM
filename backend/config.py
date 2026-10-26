from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ROBOT_NAV_", extra="ignore")

    project_root: Path = Path(r"D:\Robot_Navigation_FYP")
    data_dir: Path = Path(r"D:\Robot_Navigation_FYP\backend\data")
    results_dir: Path = Path(r"D:\Robot_Navigation_FYP\experiments\results")
    report_dir: Path = Path(r"D:\Robot_Navigation_FYP\reports\generated")
    offline_mode: bool = True
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_timeout_seconds: float = 90.0
    cors_origins: list[str] = Field(default_factory=lambda: ["http://127.0.0.1:5173", "http://localhost:5173"])

    def ensure_directories(self) -> None:
        for directory in (self.data_dir, self.results_dir, self.report_dir):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings

