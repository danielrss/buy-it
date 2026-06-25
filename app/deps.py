from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.engine import get_sessionmaker


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with get_sessionmaker()() as session:
        yield session
