from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crm_service.models import Customer
from crm_service.schemas import CustomerCreate, CustomerUpdate


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(**data.model_dump())
        self.db.add(customer)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(customer)
        return customer

    def list(self, limit: int, offset: int) -> tuple[list[Customer], int]:
        total = self.db.scalar(select(func.count()).select_from(Customer)) or 0
        customers = self.db.scalars(
            select(Customer)
            .order_by(Customer.customer_id)
            .limit(limit)
            .offset(offset)
        ).all()
        return list(customers), total

    def get(self, customer_id: int) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def update(self, customer: Customer, data: CustomerUpdate) -> Customer:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(customer, field, value)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        self.db.delete(customer)
        self.db.commit()

    def get_many(self, customer_ids: list[int]) -> list[Customer]:
        if not customer_ids:
            return []
        return list(
            self.db.scalars(
                select(Customer)
                .where(Customer.customer_id.in_(customer_ids))
                .order_by(Customer.customer_id)
            ).all()
        )

    def list_for_segment(self, criteria: dict[str, object] | None, limit: int = 1000) -> list[Customer]:
        statement = select(Customer).order_by(Customer.customer_id).limit(limit)
        criteria = criteria or {}

        loyalty_tiers = criteria.get("loyalty_tier_in")
        if isinstance(loyalty_tiers, list) and loyalty_tiers:
            statement = statement.where(Customer.loyalty_tier.in_(loyalty_tiers))

        channels = criteria.get("preferred_channel_in")
        if isinstance(channels, list) and channels:
            statement = statement.where(Customer.preferred_channel.in_(channels))

        city = criteria.get("city")
        if isinstance(city, str) and city:
            statement = statement.where(Customer.city == city)

        min_orders = criteria.get("min_total_orders")
        if isinstance(min_orders, int):
            statement = statement.where(Customer.total_orders >= min_orders)

        min_spent = criteria.get("min_total_spent")
        if isinstance(min_spent, int | float):
            statement = statement.where(Customer.total_spent >= min_spent)

        return list(self.db.scalars(statement).all())
