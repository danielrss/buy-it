import uuid

from sqlalchemy import ForeignKey, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuidv7()")
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    parent_category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("product_categories.id", ondelete="RESTRICT"),
        nullable=True,
    )
