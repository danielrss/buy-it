import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("uuidv7()")
    )
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    sku: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    product_category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("product_categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
