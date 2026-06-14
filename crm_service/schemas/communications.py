from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SendCampaignRequest(BaseModel):
    campaign_id: int = Field(..., examples=[1])
    segment_id: int | None = Field(default=None, examples=[1])
    customer_ids: list[int] | None = Field(default=None, examples=[[1, 2, 3]])
    subject: str | None = Field(default=None, examples=["A personal offer for you"])
    message: str | None = Field(default=None, examples=["Thanks for being with us."])


class SendCampaignResponse(BaseModel):
    campaign_id: int
    channel: str
    status: str
    recipients: int
    communication_ids: list[int]


class ReceiptRequest(BaseModel):
    campaign_id: int = Field(..., examples=[1])
    customer_id: int | None = Field(default=None, examples=[42])
    event_type: str = Field(..., examples=["delivered"])
    metadata: dict[str, str | int | float | bool | None] | None = Field(default=None)


class ReceiptResponse(BaseModel):
    event_id: int
    campaign_id: int
    customer_id: int | None
    event_type: str
    event_time: datetime
    metadata_json: str | None

    model_config = ConfigDict(from_attributes=True)
