from typing import Any

from pydantic import BaseModel, Field


class CampaignPlanRequest(BaseModel):
    goal: str = Field(..., examples=["Bring back inactive customers."])
    preview_limit: int = Field(default=5, ge=1, le=50)


class RecommendedAudience(BaseModel):
    name: str
    filters: dict[str, Any]
    description: str
    size: int


class RecommendedChannel(BaseModel):
    channel: str
    rationale: str


class RecommendedOffer(BaseModel):
    offer_type: str
    offer_value: str
    rationale: str


class PersonalizedMessage(BaseModel):
    subject: str
    body: str


class ExpectedPerformance(BaseModel):
    audience_size: int
    estimated_delivery_rate: float
    estimated_open_rate: float
    estimated_click_rate: float
    estimated_purchase_rate: float
    estimated_purchases: int
    estimated_revenue: float
    rationale: str


class CampaignPlanResponse(BaseModel):
    goal_understanding: str
    recommended_audience: RecommendedAudience
    audience_reasoning: str
    recommended_channel: RecommendedChannel
    recommended_offer: RecommendedOffer
    personalized_message: PersonalizedMessage
    expected_performance: ExpectedPerformance
