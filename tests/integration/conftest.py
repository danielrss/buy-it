from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.deps import get_db_session
from app.main import create_app


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    # Each test runs inside an outer transaction rolled back on teardown.
    # join_transaction_mode="create_savepoint" makes the session do all its work
    # in a SAVEPOINT, so even commits issued by the route handler are undone —
    # every test starts from the migrated-but-empty schema. NullPool avoids
    # asyncpg cross-event-loop pooling issues.
    get_settings.cache_clear()
    engine = create_async_engine(get_settings().database_url, poolclass=NullPool)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()

    await engine.dispose()


@pytest.fixture
async def client(app: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    # Wire the route's get_db_session dependency to a real session by default.
    # Tests can re-override get_db_session (e.g. a failing mock) before issuing a
    # request; overrides are cleared on teardown.
    async def _override() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
