from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "SmartBuy API"
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'smartbuy.db').as_posix()}"
    demo_mode: bool = True
    cors_origins: str = "*"
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")


settings = Settings()
