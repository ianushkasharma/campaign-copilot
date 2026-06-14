from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Campaign Copilot"
    app_env: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./data/campaign_copilot.db"

    gemini_api_key: str = Field(default="", repr=False)
    gemini_model: str = "gemini-1.5-flash"

    crm_service_host: str = "127.0.0.1"
    crm_service_port: int = 8001

    channel_service_host: str = "127.0.0.1"
    channel_service_port: int = 8002

    crm_receipt_url: str = "http://127.0.0.1:8001/receipt"
    channel_callback_retries: int = 3
    channel_min_delay_seconds: int = 1
    channel_max_delay_seconds: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
