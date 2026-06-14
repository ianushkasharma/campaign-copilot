from typing import Any

from pydantic import BaseModel, Field

from crm_service.schemas.customers import CustomerResponse


class AudienceQueryRequest(BaseModel):
    query: str = Field(
        ...,
        examples=["Find inactive customers who spent more than ₹5000"],
    )
    preview_limit: int = Field(default=10, ge=1, le=100)


class AudienceQueryResponse(BaseModel):
    audience_size: int
    reasoning: str
    filters: dict[str, Any]
    audience_preview: list[CustomerResponse]
