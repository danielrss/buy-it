from fastapi import FastAPI

from app.config import get_settings
from app.routers import health_router


def create_app() -> FastAPI:
    settings = get_settings()
    DEV_ENVIRONMENTS = ["local", "dev"]
    application = FastAPI(
        title="buy-it",
        openapi_url="/openapi.json"
        if settings.environment in DEV_ENVIRONMENTS
        else None,
        debug=settings.environment in DEV_ENVIRONMENTS,
    )

    application.include_router(health_router.router, prefix="/v1")
    return application


app = create_app()
