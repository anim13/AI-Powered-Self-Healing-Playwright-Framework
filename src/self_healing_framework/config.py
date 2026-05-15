from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_url: str = Field(default="https://example.com", alias="BASE_URL")
    browser: str = Field(default="chromium", alias="BROWSER")
    headless: bool = Field(default=True, alias="HEADLESS")
    slow_mo: int = Field(default=0, alias="SLOW_MO")
    default_timeout_ms: int = Field(default=10_000, alias="DEFAULT_TIMEOUT_MS")
    self_healing_enabled: bool = Field(default=True, alias="SELF_HEALING_ENABLED")
    ai_provider: str = Field(default="rules", alias="AI_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    reports_dir: Path = Field(default=Path("reports"), alias="REPORTS_DIR")
    artifacts_dir: Path = Field(default=Path("test-results"), alias="ARTIFACTS_DIR")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so every fixture and page object uses one config source."""

    return Settings()
