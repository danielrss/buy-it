# Architecture

## Layered design

```
HTTP request
     │
     ▼
┌─────────────┐
│   Router    │  HTTP concerns: parse input, validate, serialize response
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Service   │  Business logic: rules, orchestration, SQL queries via session
└─────────────┘
```

Architecture is kept simple for now, because we have limited business requirements. A Domain layer can be added below the service layer if needed. This should be decided ASAP, before having too much logic in the services.

**Rule:** dependencies point inward. Routers depend on services; services depend on
nothing above them. No logic leaks into routers; no HTTP concerns leak into services.

## Layers

| Folder | Role |
|---|---|
| `app/routers/` | FastAPI `APIRouter` — HTTP only: parse, validate, call service |
| `app/services/` | Business logic — orchestration, rules, SQL queries via `AsyncSession`, serialize into Pydantic models |
| `app/models/` | SQLAlchemy ORM models — table definitions, inherit from `infrastructure/db/base.py` |
| `app/schemas/` | Pydantic models — request bodies and response shapes |

## Current state

All four layers are active. Product categories (`/v1/product-categories`) is the first implemented feature. `app/services/errors.py` holds shared domain exceptions. `deps.py` is the DI wiring point for all services.

## Example: product search

This is what the layers look like once a real feature arrives.

### Model - ORM table definition

```python
# app/models/product.py
from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

### Schema - Pydantic request/response shapes

```python
# app/schemas/product_schema.py
from pydantic import BaseModel

class ProductOut(BaseModel):
    id: int
    name: str
    price: str
    in_stock: bool
```

### Service - business logic and SQL

```python
# app/services/product_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.schemas.product_schema import ProductOut

class ProductService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, q: str, page: int, page_size: int) -> list[ProductOut]:
        if not q.strip():
            return []                        # business rule lives here, not in the router
        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(Product)
            .where(Product.name.ilike(f"%{q}%"))
            .offset(offset)
            .limit(page_size)
        )
        products = rows.scalars().all()
        return [
            ProductOut(id=p.id, name=p.name,
                       price=f"{p.price} {p.currency}", in_stock=p.in_stock)
            for p in products
        ]
```

### Router - HTTP only; wires DI, delegates to service

```python
# app/routers/products_router.py
from fastapi import APIRouter, Depends, Query
from app.deps import get_product_service
from app.schemas.product_schema import ProductOut

router = APIRouter(prefix="/v1/products", tags=["products"])

@router.get("", response_model=list[ProductOut])
async def search_products(
    q: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ProductService = Depends(get_product_service),
) -> list[ProductOut]:
    return await service.search(q, page, page_size)
```

```python
# app/deps.py - the wiring point that already exists
def get_product_service(session: AsyncSession = Depends(get_db_session)) -> ProductService:
    return ProductService(session)
```

### Why this pays off

- **Testability** - `ProductService` is tested with a real or fake `AsyncSession`,
  no HTTP involved. Business rules are unit-tested in milliseconds.
- **Thin routers** - no business logic or SQL leaks into HTTP handlers.
- **Simple** - no repository indirection; the service owns the full stack from
  business rule down to SQL.
