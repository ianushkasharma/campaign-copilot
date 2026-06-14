from pydantic import BaseModel


class RFMScores(BaseModel):
    recency_days: int | None
    recency_score: int
    frequency_score: int
    monetary_score: int
    rfm_score: str


class CustomerScoreItem(BaseModel):
    customer_id: int
    name: str
    email: str
    city: str
    loyalty_tier: str
    preferred_channel: str
    total_orders: int
    total_spent: float
    rfm: RFMScores
    customer_health_score: float
    engagement_score: float


class CustomerScoresResponse(BaseModel):
    items: list[CustomerScoreItem]
    total: int


class CampaignSuccessResponse(BaseModel):
    campaign_id: int | None
    messages_sent: int
    delivered: int
    opened: int
    clicked: int
    purchased: int
    failed: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    purchase_rate: float
    revenue_generated: float
    campaign_success_score: float


class AudienceLeaderboardItem(BaseModel):
    rank: int
    segment_key: str
    ai_segment_name: str
    description: str
    audience_size: int
    messages_sent: int
    purchased: int
    conversion_rate: float
    revenue_generated: float
    campaign_success_score: float


class AudienceLeaderboardResponse(BaseModel):
    items: list[AudienceLeaderboardItem]
