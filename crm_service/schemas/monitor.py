from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CampaignEventItem(BaseModel):
    event_id: int
    campaign_id: int
    customer_id: int | None
    event_type: str
    event_time: datetime
    metadata_json: str | None

    model_config = ConfigDict(from_attributes=True)


class CampaignMonitorSummary(BaseModel):
    messages_sent: int
    delivered: int
    opened: int
    clicked: int
    purchased: int
    failed: int


class CampaignMonitorResponse(BaseModel):
    campaign_id: int | None
    summary: CampaignMonitorSummary
    timeline: list[CampaignEventItem]
