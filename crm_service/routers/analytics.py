from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from crm_service.schemas import AudienceLeaderboardResponse, CampaignSuccessResponse, CustomerScoresResponse
from crm_service.services.analytics import AnalyticsService
from shared.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/customer-scores", response_model=CustomerScoresResponse)
def customer_scores(
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> CustomerScoresResponse:
    return AnalyticsService(db).customer_scores(limit=limit, offset=offset)


@router.get("/campaign-success", response_model=CampaignSuccessResponse)
def campaign_success(
    campaign_id: int | None = None,
    db: Session = Depends(get_db),
) -> CampaignSuccessResponse:
    return AnalyticsService(db).campaign_success(campaign_id=campaign_id)


@router.get("/audience-leaderboard", response_model=AudienceLeaderboardResponse)
def audience_leaderboard(
    campaign_id: int | None = None,
    db: Session = Depends(get_db),
) -> AudienceLeaderboardResponse:
    return AnalyticsService(db).audience_leaderboard(campaign_id=campaign_id)
