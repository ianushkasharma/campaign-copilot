from fastapi import APIRouter

from crm_service.schemas import CampaignPredictionRequest, CampaignPredictionResponse
from crm_service.services import CampaignPredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post(
    "/campaign",
    response_model=CampaignPredictionResponse,
    summary="Predict campaign performance",
    description=(
        "Predicts open rate, click rate, conversion rate, and revenue from "
        "audience characteristics, channel, and offer."
    ),
)
def predict_campaign(payload: CampaignPredictionRequest) -> CampaignPredictionResponse:
    service = CampaignPredictionService()
    return service.predict(payload)
