from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
ENV_LOCAL = ROOT / ".env.local"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_LOCAL) if ENV_LOCAL.exists() else ".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = "gemini"
    llm_model: str = "antigravity-preview-05-2026"
    gemini_generation_model: str = "gemini-3.6-flash"
    llm_api_key: str = ""
    llm_base_url: str = ""

    weather_api_key: str = ""
    news_api_key: str = ""
    market_api_key: str = ""

    data_mode: str = "mix"
    enabled_domains: str = (
        "WEATHER,NEWS,TRAVEL,MARKET_DATA,SHOPPING,FINTECH,CUSTOMER_SUPPORT"
    )
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    @property
    def domains(self) -> set[str]:
        return {d.strip().upper() for d in self.enabled_domains.split(",") if d.strip()}

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_api_key.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
