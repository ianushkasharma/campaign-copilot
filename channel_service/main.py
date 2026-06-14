from fastapi import FastAPI

from channel_service.routers import health_router, send_router
from shared.config import settings
from shared.database import create_database


def create_app() -> FastAPI:
    create_database()

    app = FastAPI(
        title=f"{settings.app_name} - Channel Simulator Service",
        description=(
            "Simulates outbound marketing channel delivery and engagement, "
            "then sends event callbacks to the CRM service."
        ),
        debug=settings.debug,
        version="0.1.0",
        openapi_tags=[
            {"name": "health", "description": "Service health checks."},
            {"name": "send", "description": "Simulated channel send operations."},
        ],
    )
    app.include_router(health_router)
    app.include_router(send_router)
    return app


app = create_app()
