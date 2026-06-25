import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_product_service
from app.schemas.product_schema import ProductRead, ProductWrite
from app.services.errors import (
    DuplicateProductSku,
    DuplicateProductTitle,
    ProductCategoryNotFoundForProduct,
    ProductNotFound,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
    responses={
        status.HTTP_201_CREATED: {"description": "Product created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Product category not found"},
        status.HTTP_409_CONFLICT: {"description": "Title or SKU already exists"},
    },
)
async def create_product(
    data: ProductWrite,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    try:
        product = await service.create(data)
    except ProductCategoryNotFoundForProduct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="product category not found"
        ) from None
    except DuplicateProductTitle:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="title already exists"
        ) from None
    except DuplicateProductSku:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="sku already exists"
        ) from None
    return product


@router.get(
    "",
    response_model=list[ProductRead],
    summary="List products",
    responses={status.HTTP_200_OK: {"description": "List of products"}},
)
async def list_products(
    service: ProductService = Depends(get_product_service),
) -> list[ProductRead]:
    return await service.list()


@router.get(
    "/{id}",
    response_model=ProductRead,
    summary="Get a product",
    responses={
        status.HTTP_200_OK: {"description": "Product details"},
        status.HTTP_404_NOT_FOUND: {"description": "Product not found"},
    },
)
async def get_product(
    id: uuid.UUID,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    try:
        product = await service.get(id)
    except ProductNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        ) from None
    return product


@router.put(
    "/{id}",
    response_model=ProductRead,
    summary="Update a product",
    responses={
        status.HTTP_200_OK: {"description": "Updated product"},
        status.HTTP_400_BAD_REQUEST: {"description": "Product category not found"},
        status.HTTP_404_NOT_FOUND: {"description": "Product not found"},
        status.HTTP_409_CONFLICT: {"description": "Title or SKU already exists"},
    },
)
async def update_product(
    id: uuid.UUID,
    data: ProductWrite,
    service: ProductService = Depends(get_product_service),
) -> ProductRead:
    try:
        product = await service.update(id, data)
    except ProductNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        ) from None
    except ProductCategoryNotFoundForProduct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="product category not found"
        ) from None
    except DuplicateProductTitle:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="title already exists"
        ) from None
    except DuplicateProductSku:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="sku already exists"
        ) from None
    return product


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Product deleted"},
        status.HTTP_404_NOT_FOUND: {"description": "Product not found"},
    },
)
async def delete_product(
    id: uuid.UUID,
    service: ProductService = Depends(get_product_service),
) -> None:
    try:
        await service.delete(id)
    except ProductNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="product not found"
        ) from None
