from uuid import uuid4
from typing import Optional
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="", env_file=".env", env_file_encoding="utf-8"
    )

    # DATA CONFIGURATION POSTGRESQL
    DATABASE_NAME: Optional[str] = ""
    DATABASE_USER: Optional[str] = ""
    DATABASE_PASSWORD: Optional[str] = ""
    DATABASE_HOST: Optional[str] = ""
    DATABASE_PORT: int = Field(default=5432)
    DATABASE_SCHEMA: Optional[str] = ""

    DB_TARGET_RESULT: str
    DB_SCAN_HISTORY: str
    SECRET_AUTH_KEY: str

    # External API Keys
    SERPAPI_KEY: str
    FACECRAWLER_KEY: str
    SITE_URL: str


settings = Settings()
