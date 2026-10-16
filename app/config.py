from functools import lru_cache
import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Code Auto Agent"
    database_path: str = "./data/code_auto_agent.db"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Code Auto Agent"),
        database_path=os.getenv("DATABASE_PATH", "./data/code_auto_agent.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
