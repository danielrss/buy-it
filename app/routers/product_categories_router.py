import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_product_category_service
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
from app.services.product_category_service import ProductCategoryService

router = APIRouter(prefix="/product-categories", tags=["product-categories"])


@router.post(
    "",
    response_model=ProductCategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product category",
    responses={
        status.HTTP_201_CREATED: {"description": "Category created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Parent category not found"},
        status.HTTP_409_CONFLICT: {"description": "Category name already exists"},
    },
)
async def create_product_category(
    data: ProductCategoryWrite,
    service: ProductCategoryService = Depends(get_product_category_service),
) -> ProductCategoryRead:
    try:
        category = await service.create(data)
    except ProductCategoryParentNotFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="parent category not found"
        ) from None
    except DuplicateProductCategoryName:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="category name already exists"
        ) from None
    return category


@router.get(
    "",
    response_model=list[ProductCategoryRead],
    summary="List product categories",
    responses={status.HTTP_200_OK: {"description": "List of product categories"}},
)
async def list_product_categories(
    service: ProductCategoryService = Depends(get_product_category_service),
) -> list[ProductCategoryRead]:
    return await service.list()


@router.get(
    "/{id}",
    response_model=ProductCategoryRead,
    summary="Get a product category",
    responses={
        status.HTTP_200_OK: {"description": "Product category details"},
        status.HTTP_404_NOT_FOUND: {"description": "Category not found"},
    },
)
async def get_product_category(
    id: uuid.UUID,
    service: ProductCategoryService = Depends(get_product_category_service),
) -> ProductCategoryRead:
    try:
        category = await service.get(id)
    except ProductCategoryNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="category not found"
        ) from None

    return category


@router.put(
    "/{id}",
    response_model=ProductCategoryRead,
    summary="Update a product category",
    responses={
        status.HTTP_200_OK: {"description": "Updated product category"},
        status.HTTP_400_BAD_REQUEST: {"description": "Parent category not found"},
        status.HTTP_404_NOT_FOUND: {"description": "Category not found"},
        status.HTTP_409_CONFLICT: {"description": "Category name already exists"},
    },
)
async def update_product_category(
    id: uuid.UUID,
    data: ProductCategoryWrite,
    service: ProductCategoryService = Depends(get_product_category_service),
) -> ProductCategoryRead:
    try:
        category = await service.update(id, data)
    except ProductCategoryParentNotFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="parent category not found"
        ) from None
    except DuplicateProductCategoryName:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="category name already exists"
        ) from None
    except ProductCategoryNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="category not found"
        ) from None

    return category


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product category",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Category deleted"},
        status.HTTP_404_NOT_FOUND: {"description": "Category not found"},
        status.HTTP_409_CONFLICT: {"description": "Category has child categories"},
    },
)
async def delete_product_category(
    id: uuid.UUID,
    service: ProductCategoryService = Depends(get_product_category_service),
) -> None:
    try:
        await service.delete(id)
    except ProductCategoryHasChildren:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="category has child categories"
        ) from None
    except ProductCategoryNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="category not found"
        ) from None
