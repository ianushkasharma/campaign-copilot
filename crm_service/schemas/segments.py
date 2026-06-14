from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SegmentBase(BaseModel):
    name: str = Field(..., examples=["Inactive Customers"])
    description: str | None = Field(default=None)
    criteria_json: str | None = Field(
        default=None,
        examples=['{"loyalty_tier_in": ["Gold", "Platinum"]}'],
    )


class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    criteria_json: str | None = None


class SegmentResponse(SegmentBase):
    segment_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SegmentListResponse(BaseModel):
    items: list[SegmentResponse]
    total: int
    limit: int
    offset: int
