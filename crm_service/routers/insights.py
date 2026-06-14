from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crm_service.schemas import CampaignInsightsRequest, CampaignInsightsResponse
from crm_service.services import CampaignInsightsNotFoundError, CampaignInsightsService
from shared.database import get_db

router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])


@router.post(
    "/analyze",
    response_model=CampaignInsightsResponse,
    summary="Analyze completed campaign performance",
    description=(
        "Uses campaign event, communication, customer, and order data to generate "
        "post-campaign insights with InsightsAgent and Gemini."
    ),
)
def analyze_campaign(
    payload: CampaignInsightsRequest,
    db: Session = Depends(get_db),
) -> CampaignInsightsResponse:
    service = CampaignInsightsService(db)
    try:
        return service.analyze(payload.campaign_id)
    except CampaignInsightsNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
