import uuid

from fastapi import UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.infrastructure.logging.logger import logger
from app.infrastructure.storage.file_storage import (
    IMAGE_CONTENT_TYPES,
    ContentType,
    FileStorage,
    FileTooLarge,
    UnsupportedFileType,
)
from app.models.product import Product
from app.models.product_category import ProductCategory
from app.schemas.product_schema import (
    ProductListQuery,
    ProductRead,
    ProductSortBy,
    ProductWrite,
    SortOrder,
)
from app.services.errors import (
    DuplicateProductSku,
    DuplicateProductTitle,
    ImageTooLarge,
    InvalidImageType,
    ProductCategoryNotFoundForProduct,
    ProductNotFound,
)
from app.services.utils import escape_like_operator_value


class ProductService:
    def __init__(
        self,
        session: AsyncSession,
        storage: FileStorage | None = None,
        max_image_bytes: int = 1024 * 1024,
    ) -> None:
        self._session = session
        self._storage = storage
        self._max_image_bytes = max_image_bytes

    async def _validate_category(self, product_category_id: uuid.UUID) -> None:
        category = await self._session.get(ProductCategory, product_category_id)
        if category is None:
            raise ProductCategoryNotFoundForProduct

    async def _check_duplicate_title(
        self, title: str, exclude_id: uuid.UUID | None = None
    ) -> None:
        stmt = select(Product).where(Product.title == title)
        if exclude_id is not None:
            stmt = stmt.where(Product.id != exclude_id)
        result = await self._session.scalar(stmt)
        if result is not None:
            raise DuplicateProductTitle

    async def _check_duplicate_sku(
        self, sku: str, exclude_id: uuid.UUID | None = None
    ) -> None:
        stmt = select(Product).where(Product.sku == sku)
        if exclude_id is not None:
            stmt = stmt.where(Product.id != exclude_id)
        result = await self._session.scalar(stmt)
        if result is not None:
            raise DuplicateProductSku

    def _create_or_update_product_model(
        self, data: ProductWrite, product_model: Product | None = None
    ) -> Product:
        if product_model is None:
            product_model = Product()

        product_model.title = data.title
        product_model.description = data.description
        product_model.sku = data.sku
        product_model.price = data.price
        product_model.image_url = data.image_url
        product_model.product_category_id = data.product_category_id
        return product_model

    def _get_sort_column(self, sort_by: ProductSortBy) -> InstrumentedAttribute:
        if sort_by == ProductSortBy.PRICE:
            return Product.price
        else:
            return Product.title

    async def create(self, data: ProductWrite) -> ProductRead:
        await self._validate_category(data.product_category_id)
        await self._check_duplicate_title(data.title)
        await self._check_duplicate_sku(data.sku)

        product = self._create_or_update_product_model(data)
        self._session.add(product)
        try:
            await self._session.commit()
            await self._session.refresh(product)
        except IntegrityError:
            await self._session.rollback()
            raise DuplicateProductTitle from None
        except SQLAlchemyError:
            await self._session.rollback()
            logger.exception("There was a database error while creating a product")
            raise
        return ProductRead.model_validate(product)

    async def get(self, id: uuid.UUID) -> ProductRead:
        product = await self._session.get(Product, id)
        if product is None:
            raise ProductNotFound
        return ProductRead.model_validate(product)

    async def list(self, params: ProductListQuery) -> list[ProductRead]:
        stmt = select(Product)
        conditions = []

        # Set search and filter conditions
        if params.search:
            q = params.search
            sku_pat = "%" + escape_like_operator_value(q) + "%"
            conditions.append(
                or_(
                    Product.title.op("%")(q),
                    Product.description.op("%>")(q),
                    Product.sku.ilike(sku_pat),
                )
            )
        if params.product_category_id is not None:
            conditions.append(Product.product_category_id == params.product_category_id)
        if params.price_min is not None:
            conditions.append(Product.price >= params.price_min)
        if params.price_max is not None:
            conditions.append(Product.price <= params.price_max)
        if params.with_image is not None:
            conditions.append(
                Product.image_url.is_not(None)
                if params.with_image
                else Product.image_url.is_(None)
            )
        if conditions:
            stmt = stmt.where(*conditions)

        # Set sort order
        if params.search:
            relevance = func.greatest(
                func.similarity(Product.title, params.search),
                func.word_similarity(params.search, Product.description),
            )
            stmt = stmt.order_by(relevance.desc(), Product.title)
        else:
            sort_col = self._get_sort_column(params.sort_by)
            stmt = stmt.order_by(
                sort_col.asc()
                if params.sort_order is SortOrder.ASC
                else sort_col.desc()
            )

        result = await self._session.execute(stmt)
        return [ProductRead.model_validate(p) for p in result.scalars().all()]

    async def update(self, id: uuid.UUID, data: ProductWrite) -> ProductRead:
        product = await self._session.get(Product, id)
        if product is None:
            raise ProductNotFound

        await self._validate_category(data.product_category_id)
        await self._check_duplicate_title(data.title, exclude_id=id)
        await self._check_duplicate_sku(data.sku, exclude_id=id)

        product = self._create_or_update_product_model(data, product)
        try:
            await self._session.commit()
            await self._session.refresh(product)
        except IntegrityError:
            await self._session.rollback()
            raise DuplicateProductTitle from None
        except SQLAlchemyError:
            await self._session.rollback()
            logger.exception("There was a database error while updating a product")
            raise
        return ProductRead.model_validate(product)

    async def delete(self, id: uuid.UUID) -> None:
        product = await self._session.get(Product, id)
        if product is None:
            raise ProductNotFound
        await self._session.delete(product)
        await self._session.commit()

    async def upload_image(self, file: UploadFile) -> str:
        storage = self._storage
        if storage is None:
            raise RuntimeError("no storage configured")

        try:
            content_type = ContentType(file.content_type or "")
        except ValueError:
            raise InvalidImageType from None

        if content_type not in IMAGE_CONTENT_TYPES:
            raise InvalidImageType from None

        path = f"products/{uuid.uuid4()}"
        # Read one byte past the limit so the storage size check can reject
        # oversized uploads without buffering the whole payload.
        data = await file.read(self._max_image_bytes + 1)
        try:
            return await storage.save(
                data,
                path,
                content_type=content_type,
                max_bytes=self._max_image_bytes,
            )
        except UnsupportedFileType:
            raise InvalidImageType from None
        except FileTooLarge:
            raise ImageTooLarge from None
        except OSError:
            logger.exception("There was an error while uploading a product image")
            raise
