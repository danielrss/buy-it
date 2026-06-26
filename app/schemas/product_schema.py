import uuid
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProductSortBy(StrEnum):
    TITLE = "title"
    PRICE = "price"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class ProductWrite(BaseModel):
    title: str
    description: str | None
    sku: str
    price: Decimal = Field(gt=0, examples=[Decimal("19.99")])
    image_url: str | None
    product_category_id: uuid.UUID


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    sku: str
    price: Decimal = Field(examples=[Decimal("19.99")])
    image_url: str | None
    product_category_id: uuid.UUID


class ProductListQuery(BaseModel):
    search: str | None = None
    price_min: int | None = Field(default=None, ge=0)
    price_max: int | None = Field(default=None, ge=0)
    with_image: bool | None = None
    product_category_id: uuid.UUID | None = None
    sort_by: ProductSortBy = ProductSortBy.PRICE
    sort_order: SortOrder = SortOrder.ASC
