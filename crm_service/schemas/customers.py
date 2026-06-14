from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(..., examples=["Avery Johnson"])
    email: EmailStr = Field(..., examples=["avery.johnson@example.com"])
    phone: str | None = Field(default=None, examples=["+1-555-0134"])
    city: str = Field(..., examples=["Austin"])
    gender: str = Field(..., examples=["female"])
    preferred_channel: str = Field(..., examples=["email"])
    last_purchase_date: date | None = Field(default=None)
    total_orders: int = Field(default=0, ge=0)
    total_spent: Decimal = Field(default=Decimal("0.00"), ge=0)
    loyalty_tier: str = Field(default="Prospect", examples=["Silver"])


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    city: str | None = None
    gender: str | None = None
    preferred_channel: str | None = None
    last_purchase_date: date | None = None
    total_orders: int | None = Field(default=None, ge=0)
    total_spent: Decimal | None = Field(default=None, ge=0)
    loyalty_tier: str | None = None


class CustomerResponse(CustomerBase):
    customer_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    limit: int
    offset: int
