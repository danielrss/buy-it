import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductWrite(BaseModel):
    title: str
    description: str | None
    sku: str
    price: Decimal = Field(gt=0)
    image_url: str | None
    product_category_id: uuid.UUID


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    sku: str
    price: Decimal
    image_url: str | None
    product_category_id: uuid.UUID
