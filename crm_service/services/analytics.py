from sqlalchemy.orm import Session

from crm_service.agents import SegmentNamingAgent
from crm_service.repositories import AnalyticsRepository
from crm_service.schemas import (
    AudienceLeaderboardItem,
    AudienceLeaderboardResponse,
    CampaignSuccessResponse,
    CustomerScoreItem,
    CustomerScoresResponse,
    RFMScores,
)


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.repository = AnalyticsRepository(db)
        self.naming_agent = SegmentNamingAgent()

    def customer_scores(self, limit: int, offset: int) -> CustomerScoresResponse:
        customers, total = self.repository.customers(limit=limit, offset=offset)
        engagement = self.repository.engagement_counts([customer.customer_id for customer in customers])
        items = [self._customer_score(customer, engagement.get(customer.customer_id, {})) for customer in customers]
        return CustomerScoresResponse(items=items, total=total)

    def campaign_success(self, campaign_id: int | None) -> CampaignSuccessResponse:
        counts = self.repository.campaign_event_counts(campaign_id)
        sent = counts.get("SENT", 0)
        denominator = max(sent, 1)
        return CampaignSuccessResponse(
            campaign_id=campaign_id,
            messages_sent=sent,
            delivered=counts.get("DELIVERED", 0),
            opened=counts.get("OPENED", 0),
            clicked=counts.get("CLICKED", 0),
            purchased=counts.get("PURCHASED", 0),
            failed=counts.get("FAILED", 0),
            delivery_rate=round(counts.get("DELIVERED", 0) / denominator, 4),
            open_rate=round(counts.get("OPENED", 0) / denominator, 4),
            click_rate=round(counts.get("CLICKED", 0) / denominator, 4),
            purchase_rate=round(counts.get("PURCHASED", 0) / denominator, 4),
            revenue_generated=self.repository.campaign_revenue(campaign_id),
            campaign_success_score=self.repository.success_score(counts),
        )

    def audience_leaderboard(self, campaign_id: int | None) -> AudienceLeaderboardResponse:
        rows = self.repository.audience_leaderboard(campaign_id)
        items = []
        for index, row in enumerate(rows, start=1):
            name = self.naming_agent.name_segment(
                {
                    "loyalty_tier": row["loyalty_tier"],
                    "conversion_rate": row["conversion_rate"],
                    "revenue_generated": row["revenue_generated"],
                }
            )
            items.append(
                AudienceLeaderboardItem(
                    rank=index,
                    segment_key=str(row["loyalty_tier"]),
                    ai_segment_name=name["segment_name"],
                    description=name["description"],
                    audience_size=int(row["audience_size"]),
                    messages_sent=int(row["messages_sent"]),
                    purchased=int(row["purchased"]),
                    conversion_rate=float(row["conversion_rate"]),
                    revenue_generated=float(row["revenue_generated"]),
                    campaign_success_score=float(row["campaign_success_score"]),
                )
            )
        return AudienceLeaderboardResponse(items=items)

    def _customer_score(self, customer, engagement_counts: dict[str, int]) -> CustomerScoreItem:
        recency_days = self.repository.recency_days(customer)
        recency_score = self._recency_score(recency_days)
        frequency_score = self._frequency_score(customer.total_orders)
        monetary_score = self._monetary_score(float(customer.total_spent))
        engagement_score = self._engagement_score(
            total_orders=customer.total_orders,
            total_spent=float(customer.total_spent),
            recency_days=recency_days,
            preferred_channel=customer.preferred_channel,
            counts=engagement_counts,
        )
        health = (recency_score * 10) + (frequency_score * 8) + (monetary_score * 6) + (engagement_score * 0.18)
        return CustomerScoreItem(
            customer_id=customer.customer_id,
            name=customer.name,
            email=customer.email,
            city=customer.city,
            loyalty_tier=customer.loyalty_tier,
            preferred_channel=customer.preferred_channel,
            total_orders=customer.total_orders,
            total_spent=float(customer.total_spent),
            rfm=RFMScores(
                recency_days=recency_days,
                recency_score=recency_score,
                frequency_score=frequency_score,
                monetary_score=monetary_score,
                rfm_score=f"{recency_score}{frequency_score}{monetary_score}",
            ),
            customer_health_score=round(max(0, min(health, 100)), 2),
            engagement_score=engagement_score,
        )

    def _recency_score(self, recency_days: int | None) -> int:
        if recency_days is None or recency_days > 365:
            return 1
        if recency_days > 180:
            return 2
        if recency_days > 90:
            return 3
        if recency_days > 30:
            return 4
        return 5

    def _frequency_score(self, total_orders: int) -> int:
        if total_orders >= 12:
            return 5
        if total_orders >= 8:
            return 4
        if total_orders >= 4:
            return 3
        if total_orders >= 1:
            return 2
        return 1

    def _monetary_score(self, total_spent: float) -> int:
        if total_spent >= 5000:
            return 5
        if total_spent >= 2000:
            return 4
        if total_spent >= 750:
            return 3
        if total_spent > 0:
            return 2
        return 1

    def _engagement_score(
        self,
        total_orders: int,
        total_spent: float,
        recency_days: int | None,
        preferred_channel: str,
        counts: dict[str, int],
    ) -> float:
        frequency_component = min(total_orders / 12, 1.0) * 30
        spend_component = min(total_spent / 5000, 1.0) * 25

        if recency_days is None:
            recency_component = 0
        elif recency_days <= 30:
            recency_component = 25
        elif recency_days <= 90:
            recency_component = 20
        elif recency_days <= 180:
            recency_component = 14
        elif recency_days <= 365:
            recency_component = 8
        else:
            recency_component = 3

        channel_component = {
            "whatsapp": 10,
            "push": 9,
            "sms": 8,
            "email": 6,
            "phone": 5,
        }.get(preferred_channel.lower(), 5)

        campaign_event_bonus = min(
            counts.get("OPENED", 0) * 2
            + counts.get("CLICKED", 0) * 4
            + counts.get("PURCHASED", 0) * 8
            - counts.get("FAILED", 0) * 2,
            10,
        )

        score = frequency_component + spend_component + recency_component + channel_component + campaign_event_bonus
        return round(max(0, min(score, 100)), 2)
