from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CampaignBase(BaseModel):
    name: str = Field(..., examples=["Spring Winback"])
    channel: str = Field(..., examples=["email"])
    status: str = Field(default="draft", examples=["draft"])
    start_date: date | None = None
    end_date: date | None = None
    objective: str | None = Field(default=None, examples=["Re-engage inactive customers."])


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = None
    channel: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    objective: str | None = None


class CampaignResponse(CampaignBase):
    campaign_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignListResponse(BaseModel):
    items: list[CampaignResponse]
    total: int
    limit: int
    offset: int
