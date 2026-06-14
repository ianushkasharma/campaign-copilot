from sqlalchemy.orm import Session

from crm_service.agents import CampaignPlannerAgent
from crm_service.repositories import AudienceRepository
from crm_service.schemas import (
    AudienceCharacteristics,
    CampaignPlanRequest,
    CampaignPlanResponse,
    CampaignPredictionRequest,
    OfferInput,
)
from crm_service.services.predictions import CampaignPredictionEngine


class CampaignPlannerService:
    def __init__(self, db: Session) -> None:
        self.agent = CampaignPlannerAgent()
        self.audience_repository = AudienceRepository(db)
        self.prediction_engine = CampaignPredictionEngine()

    def plan(self, data: CampaignPlanRequest) -> CampaignPlanResponse:
        audience_result = self.agent.build_audience_filters(data.goal)
        filters = audience_result["filters"]
        audience_reasoning = str(audience_result["reasoning"])
        audience_size, preview = self.audience_repository.query_customers(
            filters=filters,
            preview_limit=data.preview_limit,
        )

        plan = self.agent.plan_campaign(
            goal=data.goal,
            audience_filters=filters,
            audience_size=audience_size,
            audience_reasoning=audience_reasoning,
        )

        recommended_audience = plan["recommended_audience"]
        if isinstance(recommended_audience, dict):
            recommended_audience["size"] = audience_size
            if preview:
                recommended_audience["description"] = (
                    f"{recommended_audience.get('description', '')} "
                    f"Preview includes customers such as {preview[0].name}."
                ).strip()

        self._apply_prediction(plan, filters, audience_size)
        return CampaignPlanResponse.model_validate(plan)

    def _apply_prediction(
        self,
        plan: dict[str, object],
        filters: dict[str, object],
        audience_size: int,
    ) -> None:
        channel = self._value_from_object(plan.get("recommended_channel"), "channel", "email")
        offer_type = self._value_from_object(
            plan.get("recommended_offer"),
            "offer_type",
            "limited_time_discount",
        )
        offer_value = self._value_from_object(
            plan.get("recommended_offer"),
            "offer_value",
            "15% off the next order",
        )

        prediction = self.prediction_engine.predict(
            CampaignPredictionRequest(
                audience=AudienceCharacteristics(
                    audience_size=audience_size,
                    inactive_days_gt=filters.get("inactive_days_gt") if isinstance(filters.get("inactive_days_gt"), int) else None,
                    filters=filters,
                ),
                channel=channel,
                offer=OfferInput(offer_type=offer_type, offer_value=offer_value),
            )
        )

        plan["expected_performance"] = {
            "audience_size": audience_size,
            "estimated_delivery_rate": 0.92,
            "estimated_open_rate": prediction.predicted_open_rate,
            "estimated_click_rate": prediction.predicted_click_rate,
            "estimated_purchase_rate": prediction.predicted_conversion_rate,
            "estimated_purchases": round(audience_size * prediction.predicted_conversion_rate),
            "estimated_revenue": prediction.predicted_revenue,
            "rationale": "Prediction engine estimate. " + " ".join(prediction.assumptions),
        }

    def _value_from_object(self, value: object, key: str, default: str) -> str:
        if isinstance(value, dict):
            raw_value = value.get(key)
            if raw_value:
                return str(raw_value)
        return default
