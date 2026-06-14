from pydantic import BaseModel, Field


class InsightDetail(BaseModel):
    name: str
    reason: str


class CampaignInsightsRequest(BaseModel):
    campaign_id: int = Field(..., examples=[1])


class CampaignInsightsResponse(BaseModel):
    campaign_id: int
    what_happened: str
    why_it_happened: str
    best_segment: InsightDetail
    worst_segment: InsightDetail
    best_channel: InsightDetail
    revenue_generated: float
    recommended_next_action: str
    metrics: dict[str, int | float]
