from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.infrastructure.db.engine import get_sessionmaker
from app.infrastructure.storage.file_storage import FileStorage
from app.infrastructure.storage.local_file_storage import LocalFileStorage
from app.services.product_category_service import ProductCategoryService
from app.services.product_service import ProductService


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with get_sessionmaker()() as session:
        yield session


def get_product_category_service(
    session: AsyncSession = Depends(get_db_session),
) -> ProductCategoryService:
    return ProductCategoryService(session)


def get_file_storage() -> FileStorage:
    s = get_settings()
    return LocalFileStorage(s.media_root, s.media_url_prefix)


def get_product_service(
    session: AsyncSession = Depends(get_db_session),
    storage: FileStorage = Depends(get_file_storage),
) -> ProductService:
    return ProductService(session, storage, get_settings().max_image_bytes)
