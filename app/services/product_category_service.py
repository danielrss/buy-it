import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.logging.logger import logger
from app.models.product_category import ProductCategory
from app.schemas.product_category_schema import (
    ProductCategoryRead,
    ProductCategoryWrite,
)
from app.services.errors import (
    DuplicateProductCategoryName,
    ProductCategoryHasChildren,
    ProductCategoryNotFound,
    ProductCategoryParentNotFound,
)


class ProductCategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _create_or_update_product_category_model(
        self, data: ProductCategoryWrite, category_model: ProductCategory | None = None
    ) -> ProductCategory:
        if category_model is None:
            category_model = ProductCategory()

        category_model.name = data.name
        category_model.parent_category_id = data.parent_category_id
        return category_model

    async def create(self, data: ProductCategoryWrite) -> ProductCategoryRead:
        if data.parent_category_id is not None:
            parent = await self._session.get(ProductCategory, data.parent_category_id)
            if parent is None:
                raise ProductCategoryParentNotFound

        category = self._create_or_update_product_category_model(data)
        self._session.add(category)
        try:
            await self._session.commit()
            await self._session.refresh(category)
        except IntegrityError:
            await self._session.rollback()
            raise DuplicateProductCategoryName from None
        except SQLAlchemyError:
            await self._session.rollback()
            logger.exception(
                "There was a database error while creating a product category"
            )
            raise
        return ProductCategoryRead.model_validate(category)

    async def get(self, id: uuid.UUID) -> ProductCategoryRead:
        category = await self._session.get(ProductCategory, id)
        if category is None:
            raise ProductCategoryNotFound

        return ProductCategoryRead.model_validate(category)

    async def list(self) -> list[ProductCategoryRead]:
        result = await self._session.execute(
            select(ProductCategory).order_by(ProductCategory.name)
        )
        return [ProductCategoryRead.model_validate(c) for c in result.scalars().all()]

    async def update(
        self, id: uuid.UUID, data: ProductCategoryWrite
    ) -> ProductCategoryRead:
        category = await self._session.get(ProductCategory, id)
        if category is None:
            raise ProductCategoryNotFound

        if data.parent_category_id == id:
            raise ProductCategoryParentNotFound

        if data.parent_category_id is not None:
            parent = await self._session.get(ProductCategory, data.parent_category_id)
            if parent is None:
                raise ProductCategoryParentNotFound

        category = self._create_or_update_product_category_model(data, category)
        try:
            await self._session.commit()
            await self._session.refresh(category)
        except IntegrityError:
            await self._session.rollback()
            raise DuplicateProductCategoryName from None
        except SQLAlchemyError:
            await self._session.rollback()
            logger.exception(
                "There was a database error while updating a product category"
            )
            raise
        return ProductCategoryRead.model_validate(category)

    async def delete(self, id: uuid.UUID) -> None:
        category = await self._session.get(ProductCategory, id)
        if category is None:
            raise ProductCategoryNotFound

        child_count = await self._session.scalar(
            select(func.count()).where(ProductCategory.parent_category_id == id)
        )
        if child_count:
            raise ProductCategoryHasChildren

        await self._session.delete(category)
        await self._session.commit()
