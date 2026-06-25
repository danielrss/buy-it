from fastapi import FastAPI

from app.routers import health
from app.config import get_settings


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

    print(settings.environment)
    application.include_router(health.router)
    return application


app = create_app()
