from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db_session
from app.infrastructure.db.health import check_database
from app.schemas.health_schema import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Application health",
    responses={status.HTTP_200_OK: {"description": "Application is healthy"}},
)
async def get_health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/db",
    response_model=HealthResponse,
    summary="Database health",
    responses={
        status.HTTP_200_OK: {"description": "Database is healthy"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database unavailable"},
    },
)
async def get_db_health(
    session: AsyncSession = Depends(get_db_session),
) -> HealthResponse:
    if not await check_database(session):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        )
    return HealthResponse(status="ok")
