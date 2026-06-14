from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from crm_service.models import Customer


class AudienceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def query_customers(
        self,
        filters: dict[str, object],
        preview_limit: int,
    ) -> tuple[int, list[Customer]]:
        statement = self._apply_filters(select(Customer), filters)
        count_statement = self._apply_filters(select(func.count()).select_from(Customer), filters)

        total = self.db.scalar(count_statement) or 0
        preview = self.db.scalars(
            statement.order_by(Customer.total_spent.desc(), Customer.customer_id).limit(preview_limit)
        ).all()
        return total, list(preview)

    def _apply_filters(self, statement, filters: dict[str, object]):
        inactive_days = filters.get("inactive_days_gt")
        if isinstance(inactive_days, int):
            cutoff = date.today() - timedelta(days=inactive_days)
            statement = statement.where(
                or_(
                    Customer.last_purchase_date.is_(None),
                    Customer.last_purchase_date < cutoff,
                    Customer.loyalty_tier == "Inactive",
                )
            )

        if "total_spent_gt" in filters:
            statement = statement.where(Customer.total_spent > Decimal(str(filters["total_spent_gt"])))

        if "total_spent_gte" in filters:
            statement = statement.where(Customer.total_spent >= Decimal(str(filters["total_spent_gte"])))

        if "total_spent_lt" in filters:
            statement = statement.where(Customer.total_spent < Decimal(str(filters["total_spent_lt"])))

        if "total_orders_gt" in filters:
            statement = statement.where(Customer.total_orders > int(filters["total_orders_gt"]))

        if "total_orders_gte" in filters:
            statement = statement.where(Customer.total_orders >= int(filters["total_orders_gte"]))

        loyalty_tiers = filters.get("loyalty_tier_in")
        if isinstance(loyalty_tiers, list) and loyalty_tiers:
            statement = statement.where(Customer.loyalty_tier.in_(loyalty_tiers))

        channels = filters.get("preferred_channel_in")
        if isinstance(channels, list) and channels:
            statement = statement.where(Customer.preferred_channel.in_([str(channel).lower() for channel in channels]))

        city = filters.get("city")
        if isinstance(city, str):
            statement = statement.where(Customer.city == city)

        gender = filters.get("gender")
        if isinstance(gender, str):
            statement = statement.where(Customer.gender == gender)

        return statement
