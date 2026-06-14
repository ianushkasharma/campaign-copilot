from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models import Base, TimestampMixin


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("email", name="uq_customers_email"),)

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(30), nullable=False)
    preferred_channel: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    last_purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    loyalty_tier: Mapped[str] = mapped_column(String(30), index=True, nullable=False)

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    communications: Mapped[list["Communication"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    campaign_events: Mapped[list["CampaignEvent"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="orders")


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"

    campaign_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)

    communications: Mapped[list["Communication"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan",
    )
    campaign_events: Mapped[list["CampaignEvent"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan",
    )


class Communication(TimestampMixin, Base):
    __tablename__ = "communications"

    communication_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    campaign_id: Mapped[int | None] = mapped_column(
        ForeignKey("campaigns.campaign_id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    channel: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), index=True, nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="communications")
    campaign: Mapped["Campaign"] = relationship(back_populates="communications")


class CampaignEvent(TimestampMixin, Base):
    __tablename__ = "campaign_events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.campaign_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.customer_id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="campaign_events")
    customer: Mapped["Customer"] = relationship(back_populates="campaign_events")


class Segment(TimestampMixin, Base):
    __tablename__ = "segments"

    segment_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria_json: Mapped[str | None] = mapped_column(Text, nullable=True)
