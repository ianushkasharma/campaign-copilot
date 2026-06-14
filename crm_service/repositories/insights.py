from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from crm_service.models import CampaignEvent, Communication, Customer, Order


class CampaignInsightsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def campaign_dataset(self, campaign_id: int) -> dict[str, object]:
        event_counts = self._event_counts(campaign_id)
        sent_customers = self._sent_customers(campaign_id)
        purchased_customers = self._purchased_customers(campaign_id)
        segment_stats = self._segment_stats(sent_customers, purchased_customers)
        channel_stats = self._channel_stats(campaign_id)
        revenue = self._revenue_generated(sent_customers, event_counts.get("PURCHASED", 0))

        return {
            "campaign_id": campaign_id,
            "summary": {
                "messages_sent": event_counts.get("SENT", 0),
                "delivered": event_counts.get("DELIVERED", 0),
                "opened": event_counts.get("OPENED", 0),
                "clicked": event_counts.get("CLICKED", 0),
                "purchased": event_counts.get("PURCHASED", 0),
                "failed": event_counts.get("FAILED", 0),
            },
            "segment_stats": segment_stats,
            "channel_stats": channel_stats,
            "best_segment": self._best_segment(segment_stats),
            "worst_segment": self._worst_segment(segment_stats),
            "best_channel": self._best_channel(channel_stats),
            "revenue_generated": revenue,
        }

    def _event_counts(self, campaign_id: int) -> dict[str, int]:
        rows = self.db.execute(
            select(CampaignEvent.event_type, func.count())
            .where(CampaignEvent.campaign_id == campaign_id)
            .group_by(CampaignEvent.event_type)
        ).all()
        return {str(event_type).upper(): int(count) for event_type, count in rows}

    def _sent_customers(self, campaign_id: int) -> list[Customer]:
        return list(
            self.db.scalars(
                select(Customer)
                .join(Communication, Communication.customer_id == Customer.customer_id)
                .where(Communication.campaign_id == campaign_id)
            ).all()
        )

    def _purchased_customers(self, campaign_id: int) -> set[int]:
        rows = self.db.scalars(
            select(CampaignEvent.customer_id)
            .where(CampaignEvent.campaign_id == campaign_id)
            .where(CampaignEvent.event_type == "PURCHASED")
            .where(CampaignEvent.customer_id.is_not(None))
        ).all()
        return {int(customer_id) for customer_id in rows}

    def _segment_stats(self, sent_customers: list[Customer], purchased_customer_ids: set[int]) -> list[dict[str, object]]:
        by_tier: dict[str, dict[str, int]] = defaultdict(lambda: {"sent": 0, "purchased": 0})
        for customer in sent_customers:
            tier = customer.loyalty_tier or "Unknown"
            by_tier[tier]["sent"] += 1
            if customer.customer_id in purchased_customer_ids:
                by_tier[tier]["purchased"] += 1

        stats = []
        for tier, values in by_tier.items():
            sent = values["sent"]
            purchased = values["purchased"]
            stats.append(
                {
                    "segment": tier,
                    "sent": sent,
                    "purchased": purchased,
                    "conversion_rate": purchased / sent if sent else 0,
                }
            )
        return sorted(stats, key=lambda item: (item["conversion_rate"], item["sent"]), reverse=True)

    def _channel_stats(self, campaign_id: int) -> list[dict[str, object]]:
        rows = self.db.execute(
            select(Communication.channel, func.count())
            .where(Communication.campaign_id == campaign_id)
            .group_by(Communication.channel)
        ).all()
        purchased = self._event_counts(campaign_id).get("PURCHASED", 0)
        stats = []
        for channel, sent in rows:
            sent_count = int(sent)
            stats.append(
                {
                    "channel": str(channel),
                    "sent": sent_count,
                    "purchased": purchased,
                    "conversion_rate": purchased / sent_count if sent_count else 0,
                }
            )
        return sorted(stats, key=lambda item: item["conversion_rate"], reverse=True)

    def _revenue_generated(self, sent_customers: list[Customer], purchase_count: int) -> float:
        customer_ids = [customer.customer_id for customer in sent_customers]
        if not customer_ids or purchase_count == 0:
            return 0.0

        average_order_value = self.db.scalar(
            select(func.avg(Order.amount)).where(Order.customer_id.in_(customer_ids))
        )
        value = Decimal(str(average_order_value or 75))
        return round(float(value) * purchase_count, 2)

    def _best_segment(self, segment_stats: list[dict[str, object]]) -> dict[str, str]:
        if not segment_stats:
            return {"name": "Unknown", "reason": "No segment performance data is available."}
        segment = segment_stats[0]
        return {
            "name": str(segment["segment"]),
            "reason": f"Highest conversion rate at {float(segment['conversion_rate']):.1%}.",
        }

    def _worst_segment(self, segment_stats: list[dict[str, object]]) -> dict[str, str]:
        if not segment_stats:
            return {"name": "Unknown", "reason": "No segment performance data is available."}
        segment = sorted(segment_stats, key=lambda item: (item["conversion_rate"], -item["sent"]))[0]
        return {
            "name": str(segment["segment"]),
            "reason": f"Lowest conversion rate at {float(segment['conversion_rate']):.1%}.",
        }

    def _best_channel(self, channel_stats: list[dict[str, object]]) -> dict[str, str]:
        if not channel_stats:
            return {"name": "Unknown", "reason": "No channel performance data is available."}
        channel = channel_stats[0]
        return {
            "name": str(channel["channel"]),
            "reason": f"Highest observed conversion rate at {float(channel['conversion_rate']):.1%}.",
        }
