from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import health_router, product_categories_router, products_router


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
    application.include_router(product_categories_router.router, prefix="/v1")
    application.include_router(products_router.router, prefix="/v1")

    settings.media_root.mkdir(parents=True, exist_ok=True)
    application.mount(
        settings.media_url_prefix,
        StaticFiles(directory=settings.media_root),
        name="media",
    )

    return application


app = create_app()
