from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crm_service.schemas import CampaignPlanRequest, CampaignPlanResponse
from crm_service.services import CampaignPlannerService
from shared.database import get_db

router = APIRouter(prefix="/campaign-copilot", tags=["campaign-copilot"])


@router.post(
    "/plan",
    response_model=CampaignPlanResponse,
    summary="Generate an AI campaign plan",
    description=(
        "Uses CampaignPlannerAgent to understand the campaign goal, recommend "
        "an audience, channel, offer, message, and expected performance."
    ),
)
def plan_campaign(payload: CampaignPlanRequest, db: Session = Depends(get_db)) -> CampaignPlanResponse:
    service = CampaignPlannerService(db)
    return service.plan(payload)
