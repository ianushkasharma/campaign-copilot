from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SendRequest(BaseModel):
    recipient: str = Field(..., examples=["avery.johnson@example.com"])
    message: str = Field(..., examples=["Your early access offer is ready."])
    channel: str = Field(..., examples=["email"])
    campaign_id: int = Field(..., examples=[1])


class SendResponse(BaseModel):
    event_id: int
    campaign_id: int
    recipient: str
    channel: str
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)


class ChannelEventResponse(BaseModel):
    event_id: int
    campaign_id: int
    recipient: str
    channel: str
    status: str
    attempts: int
    last_error: str | None
    last_event_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
