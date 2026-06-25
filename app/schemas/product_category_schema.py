import uuid

from pydantic import BaseModel, ConfigDict


class ProductCategoryWrite(BaseModel):
    name: str
    parent_category_id: uuid.UUID | None = None


class ProductCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    parent_category_id: uuid.UUID | None
