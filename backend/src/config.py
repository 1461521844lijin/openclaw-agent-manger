"""Application configuration"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 3789
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/agents.db"

    # OpenClaw
    openclaw_api_key: str = ""
    openclaw_workspace: str = "./workspace"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure data directory exists
(BASE_DIR / "data").mkdir(exist_ok=True)

# Settings instance
settings = Settings()
