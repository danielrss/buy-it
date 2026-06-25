from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.engine import get_sessionmaker
from app.services.product_category_service import ProductCategoryService


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with get_sessionmaker()() as session:
        yield session


def get_product_category_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProductCategoryService:
    return ProductCategoryService(session)
