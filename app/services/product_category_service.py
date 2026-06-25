import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def create(self, data: ProductCategoryWrite) -> ProductCategoryRead:
        if data.parent_category_id is not None:
            parent = await self._session.get(ProductCategory, data.parent_category_id)
            if parent is None:
                raise ProductCategoryParentNotFound

        category = ProductCategory(
            name=data.name,
            parent_category_id=data.parent_category_id,
        )
        self._session.add(category)
        try:
            await self._session.commit()
            await self._session.refresh(category)
        except IntegrityError:
            await self._session.rollback()
            raise DuplicateProductCategoryName from None
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

        category.name = data.name
        category.parent_category_id = data.parent_category_id
        try:
            await self._session.commit()
            await self._session.refresh(category)
        except IntegrityError:
            await self._session.rollback()
            raise DuplicateProductCategoryName from None
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
