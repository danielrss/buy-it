from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "local"

    postgres_user: str = "buyit"
    postgres_password: str = "buyit"
    postgres_db: str = "buyit"
    postgres_host: str = "db"
    postgres_port: int = 5432

    media_root: Path = Path("media")
    media_url_prefix: str = "/media"
    max_image_bytes: int = 1024 * 1024

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
