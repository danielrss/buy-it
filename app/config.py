from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
