from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from crm_service.schemas import CampaignMonitorResponse
from crm_service.services import CampaignMonitorService
from shared.database import get_db

router = APIRouter(prefix="/campaign-monitor", tags=["campaign-monitor"])


@router.get(
    "",
    response_model=CampaignMonitorResponse,
    summary="Get campaign event monitor metrics",
    description="Aggregates messages sent, delivered, opened, clicked, purchased, and failed from campaign_events.",
)
def get_campaign_monitor(
    campaign_id: int | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    db: Session = Depends(get_db),
) -> CampaignMonitorResponse:
    service = CampaignMonitorService(db)
    return service.get_monitor(campaign_id=campaign_id, limit=limit)
