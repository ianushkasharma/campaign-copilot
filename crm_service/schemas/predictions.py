from typing import Any

from pydantic import BaseModel, Field


class AudienceCharacteristics(BaseModel):
    audience_size: int = Field(..., ge=0, examples=[1250])
    avg_total_spent: float | None = Field(default=None, ge=0, examples=[6200])
    avg_total_orders: float | None = Field(default=None, ge=0, examples=[4.5])
    inactive_days_gt: int | None = Field(default=None, ge=0, examples=[180])
    loyalty_tier_mix: dict[str, float] | None = Field(default=None)
    preferred_channel_mix: dict[str, float] | None = Field(default=None)
    filters: dict[str, Any] | None = Field(default=None)


class OfferInput(BaseModel):
    offer_type: str = Field(..., examples=["limited_time_discount"])
    offer_value: str = Field(..., examples=["15% off the next order"])


class CampaignPredictionRequest(BaseModel):
    audience: AudienceCharacteristics
    channel: str = Field(..., examples=["whatsapp"])
    offer: OfferInput


class CampaignPredictionResponse(BaseModel):
    predicted_open_rate: float
    predicted_click_rate: float
    predicted_conversion_rate: float
    predicted_revenue: float
    assumptions: list[str]
