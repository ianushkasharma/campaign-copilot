from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from crm_service.models import CampaignEvent, Communication, Customer, Order


class AnalyticsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def customers(self, limit: int, offset: int) -> tuple[list[Customer], int]:
        total = self.db.scalar(select(func.count()).select_from(Customer)) or 0
        items = self.db.scalars(select(Customer).order_by(Customer.customer_id).limit(limit).offset(offset)).all()
        return list(items), total

    def engagement_counts(self, customer_ids: list[int]) -> dict[int, dict[str, int]]:
        if not customer_ids:
            return {}
        rows = self.db.execute(
            select(CampaignEvent.customer_id, CampaignEvent.event_type, func.count())
            .where(CampaignEvent.customer_id.in_(customer_ids))
            .group_by(CampaignEvent.customer_id, CampaignEvent.event_type)
        ).all()
        counts: dict[int, dict[str, int]] = defaultdict(dict)
        for customer_id, event_type, count in rows:
            if customer_id is not None:
                counts[int(customer_id)][str(event_type).upper()] = int(count)
        return counts

    def campaign_event_counts(self, campaign_id: int | None = None) -> dict[str, int]:
        statement = select(CampaignEvent.event_type, func.count()).group_by(CampaignEvent.event_type)
        if campaign_id is not None:
            statement = statement.where(CampaignEvent.campaign_id == campaign_id)
        rows = self.db.execute(statement).all()
        return {str(event_type).upper(): int(count) for event_type, count in rows}

    def campaign_revenue(self, campaign_id: int | None = None) -> float:
        purchased_count = self.campaign_event_counts(campaign_id).get("PURCHASED", 0)
        if purchased_count == 0:
            return 0.0
        average_order_value = self.db.scalar(select(func.avg(Order.amount))) or Decimal("75")
        return round(float(average_order_value) * purchased_count, 2)

    def audience_leaderboard(self, campaign_id: int | None = None) -> list[dict[str, object]]:
        statement = (
            select(Customer.loyalty_tier, CampaignEvent.event_type, func.count())
            .join(CampaignEvent, CampaignEvent.customer_id == Customer.customer_id)
            .group_by(Customer.loyalty_tier, CampaignEvent.event_type)
        )
        if campaign_id is not None:
            statement = statement.where(CampaignEvent.campaign_id == campaign_id)

        rows = self.db.execute(statement).all()
        grouped: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for tier, event_type, count in rows:
            grouped[str(tier or "Unknown")][str(event_type).upper()] += int(count)

        average_order_value = float(self.db.scalar(select(func.avg(Order.amount))) or 75)
        leaderboard = []
        for tier, counts in grouped.items():
            sent = counts.get("SENT", 0)
            purchased = counts.get("PURCHASED", 0)
            conversion = purchased / sent if sent else 0.0
            leaderboard.append(
                {
                    "loyalty_tier": tier,
                    "audience_size": sent,
                    "messages_sent": sent,
                    "purchased": purchased,
                    "conversion_rate": conversion,
                    "revenue_generated": round(purchased * average_order_value, 2),
                    "campaign_success_score": self.success_score(counts),
                }
            )
        return sorted(leaderboard, key=lambda item: (item["campaign_success_score"], item["revenue_generated"]), reverse=True)

    def success_score(self, counts: dict[str, int]) -> float:
        sent = max(counts.get("SENT", 0), 1)
        delivered = counts.get("DELIVERED", 0) / sent
        opened = counts.get("OPENED", 0) / sent
        clicked = counts.get("CLICKED", 0) / sent
        purchased = counts.get("PURCHASED", 0) / sent
        failed = counts.get("FAILED", 0) / sent
        score = (delivered * 20) + (opened * 25) + (clicked * 25) + (purchased * 35) - (failed * 20)
        return round(max(0, min(score, 100)), 2)

    def recency_days(self, customer: Customer) -> int | None:
        if customer.last_purchase_date is None:
            return None
        return (date.today() - customer.last_purchase_date).days
