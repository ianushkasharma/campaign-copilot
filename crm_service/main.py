from fastapi import FastAPI

from crm_service.routers import (
    campaigns_router,
    campaign_planner_router,
    audiences_router,
    analytics_router,
    communications_router,
    customers_router,
    health_router,
    insights_router,
    monitor_router,
    predictions_router,
    segments_router,
)
from shared.config import settings
from shared.database import create_database


def create_app() -> FastAPI:
    create_database()

    app = FastAPI(
        title=f"{settings.app_name} - CRM Service",
        description=(
            "CRM APIs for managing customers, campaigns, segments, "
            "campaign sends, and campaign event receipts."
        ),
        debug=settings.debug,
        version="0.1.0",
        contact={"name": "Campaign Copilot"},
        openapi_tags=[
            {"name": "health", "description": "Service health checks."},
            {"name": "customers", "description": "Customer profile CRUD operations."},
            {"name": "campaigns", "description": "Campaign CRUD operations."},
            {"name": "segments", "description": "Audience segment operations."},
            {"name": "communications", "description": "Campaign send and receipt workflows."},
            {"name": "audiences", "description": "AI-powered audience segmentation."},
            {"name": "campaign-copilot", "description": "AI campaign planning workflows."},
            {"name": "predictions", "description": "Campaign performance prediction APIs."},
            {"name": "campaign-monitor", "description": "Campaign event monitoring APIs."},
            {"name": "ai-insights", "description": "AI post-campaign analysis APIs."},
            {"name": "analytics", "description": "RFM, scoring, and leaderboard analytics."},
        ],
    )
    app.include_router(health_router)
    app.include_router(customers_router)
    app.include_router(campaigns_router)
    app.include_router(segments_router)
    app.include_router(communications_router)
    app.include_router(audiences_router)
    app.include_router(campaign_planner_router)
    app.include_router(predictions_router)
    app.include_router(monitor_router)
    app.include_router(insights_router)
    app.include_router(analytics_router)
    return app


app = create_app()
