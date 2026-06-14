"""CRM service API routers."""

from crm_service.routers.audiences import router as audiences_router
from crm_service.routers.analytics import router as analytics_router
from crm_service.routers.campaigns import router as campaigns_router
from crm_service.routers.campaign_planner import router as campaign_planner_router
from crm_service.routers.communications import router as communications_router
from crm_service.routers.customers import router as customers_router
from crm_service.routers.health import router as health_router
from crm_service.routers.insights import router as insights_router
from crm_service.routers.monitor import router as monitor_router
from crm_service.routers.predictions import router as predictions_router
from crm_service.routers.segments import router as segments_router

__all__ = [
    "campaigns_router",
    "campaign_planner_router",
    "audiences_router",
    "analytics_router",
    "communications_router",
    "customers_router",
    "health_router",
    "insights_router",
    "monitor_router",
    "predictions_router",
    "segments_router",
]
