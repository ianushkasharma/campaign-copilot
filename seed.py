from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from faker import Faker
from sqlalchemy import func, select

from crm_service.models import Campaign, Customer, Order, Segment
from shared.database import SessionLocal, create_database, drop_database

CUSTOMER_COUNT = 5000
ORDER_COUNT = 20000

CHANNELS = ["email", "sms", "whatsapp", "push", "phone"]
CATEGORIES = [
    "Apparel",
    "Beauty",
    "Electronics",
    "Fitness",
    "Grocery",
    "Home",
    "Luxury",
    "Outdoor",
    "Pet Care",
    "Travel",
]
CITIES = [
    "New York",
    "Los Angeles",
    "Chicago",
    "Houston",
    "Phoenix",
    "Philadelphia",
    "San Antonio",
    "San Diego",
    "Dallas",
    "San Jose",
    "Austin",
    "Jacksonville",
    "Fort Worth",
    "Columbus",
    "Charlotte",
    "San Francisco",
    "Seattle",
    "Denver",
    "Boston",
    "Miami",
]

fake = Faker()


def weighted_choice(choices: list[tuple[str, float]]) -> str:
    labels, weights = zip(*choices, strict=True)
    return random.choices(labels, weights=weights, k=1)[0]


def customer_profile() -> str:
    return weighted_choice(
        [
            ("inactive", 0.16),
            ("casual", 0.54),
            ("steady", 0.22),
            ("loyal", 0.08),
        ]
    )


def customer_profile_for_id(customer_id: int) -> str:
    if customer_id <= 160:
        return "inactive_high_value"
    if customer_id <= 320:
        return "high_spend"
    if customer_id <= 560:
        return "loyal"
    return customer_profile()


def preferred_channel(profile: str) -> str:
    if profile == "inactive_high_value":
        weights = [("email", 0.32), ("sms", 0.16), ("whatsapp", 0.34), ("push", 0.08), ("phone", 0.1)]
    elif profile == "inactive":
        weights = [("email", 0.45), ("sms", 0.2), ("whatsapp", 0.12), ("push", 0.08), ("phone", 0.15)]
    elif profile == "high_spend":
        weights = [("email", 0.28), ("sms", 0.12), ("whatsapp", 0.34), ("push", 0.2), ("phone", 0.06)]
    elif profile == "loyal":
        weights = [("email", 0.22), ("sms", 0.16), ("whatsapp", 0.3), ("push", 0.26), ("phone", 0.06)]
    else:
        weights = [("email", 0.34), ("sms", 0.2), ("whatsapp", 0.22), ("push", 0.18), ("phone", 0.06)]
    return weighted_choice(weights)


def order_amount(profile: str) -> Decimal:
    if profile == "inactive_high_value":
        amount = random.uniform(550, 950)
    elif profile == "high_spend":
        amount = random.uniform(600, 1200)
    elif profile == "inactive":
        amount = random.lognormvariate(3.3, 0.45)
    elif profile == "loyal":
        amount = random.lognormvariate(4.8, 0.55)
    elif profile == "steady":
        amount = random.lognormvariate(4.2, 0.5)
    else:
        amount = random.lognormvariate(3.7, 0.55)
    return Decimal(str(round(min(max(amount, 8), 1500), 2)))


def order_date(profile: str) -> date:
    today = date.today()
    if profile == "inactive_high_value":
        return today - timedelta(days=random.randint(390, 720))
    if profile == "inactive":
        return today - timedelta(days=random.randint(180, 900))
    if profile == "high_spend":
        return today - timedelta(days=random.randint(0, 160))
    if profile == "loyal":
        return today - timedelta(days=random.randint(0, 120))
    if profile == "steady":
        return today - timedelta(days=random.randint(0, 240))
    return today - timedelta(days=random.randint(0, 540))


def loyalty_tier(total_orders: int, total_spent: Decimal, last_purchase_date: date | None) -> str:
    if last_purchase_date is None:
        return "Prospect"

    inactive_days = (date.today() - last_purchase_date).days
    if inactive_days > 365:
        return "Inactive"
    if total_orders >= 12 or total_spent >= Decimal("1500"):
        return "Platinum"
    if total_orders >= 6 or total_spent >= Decimal("700"):
        return "Gold"
    if total_orders >= 2 or total_spent >= Decimal("150"):
        return "Silver"
    return "Bronze"


def engagement_score(
    total_orders: int,
    total_spent: Decimal,
    last_purchase_date: date | None,
    preferred_channel_value: str,
) -> float:
    frequency_component = min(total_orders / 12, 1.0) * 30
    spend_component = min(float(total_spent) / 5000, 1.0) * 25

    if last_purchase_date is None:
        recency_component = 0
    else:
        recency_days = (date.today() - last_purchase_date).days
        if recency_days <= 30:
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
    }.get(preferred_channel_value.lower(), 5)

    profile_noise = random.uniform(-4, 4)
    score = frequency_component + spend_component + recency_component + channel_component + profile_noise
    return round(max(0, min(score, 100)), 2)


def create_customers() -> tuple[list[Customer], dict[int, str]]:
    customers: list[Customer] = []
    profiles: dict[int, str] = {}
    used_emails: set[str] = set()

    for customer_id in range(1, CUSTOMER_COUNT + 1):
        profile = customer_profile_for_id(customer_id)
        email = fake.unique.email()
        while email in used_emails:
            email = fake.unique.email()
        used_emails.add(email)

        gender = weighted_choice([("female", 0.49), ("male", 0.48), ("non_binary", 0.03)])
        customer = Customer(
            customer_id=customer_id,
            name=fake.name_female() if gender == "female" else fake.name_male() if gender == "male" else fake.name(),
            email=email,
            phone=fake.phone_number() if random.random() > 0.08 else None,
            city=random.choice(CITIES),
            gender=gender,
            preferred_channel=preferred_channel(profile),
            last_purchase_date=None,
            total_orders=0,
            total_spent=Decimal("0.00"),
            loyalty_tier="Prospect",
        )
        customers.append(customer)
        profiles[customer_id] = profile

    return customers, profiles


def weighted_customer_ids(profiles: dict[int, str]) -> list[int]:
    pool: list[int] = []
    for customer_id, profile in profiles.items():
        if profile == "inactive_high_value":
            repeats = 5
        elif profile == "high_spend":
            repeats = 8
        elif profile == "inactive":
            repeats = 1
        elif profile == "casual":
            repeats = 3
        elif profile == "steady":
            repeats = 7
        else:
            repeats = 16
        pool.extend([customer_id] * repeats)
    return pool


def guaranteed_order_count(profile: str) -> int:
    if profile == "inactive_high_value":
        return 10
    if profile == "high_spend":
        return 9
    if profile == "loyal":
        return 8
    return 0


def create_orders(profiles: dict[int, str]) -> list[Order]:
    orders: list[Order] = []
    customer_pool = weighted_customer_ids(profiles)
    order_id = 1

    for customer_id, profile in profiles.items():
        for _ in range(guaranteed_order_count(profile)):
            orders.append(
                Order(
                    order_id=order_id,
                    customer_id=customer_id,
                    amount=order_amount(profile),
                    date=order_date(profile),
                    category=random.choice(CATEGORIES),
                )
            )
            order_id += 1

    while order_id <= ORDER_COUNT:
        customer_id = random.choice(customer_pool)
        profile = profiles[customer_id]
        orders.append(
            Order(
                order_id=order_id,
                customer_id=customer_id,
                amount=order_amount(profile),
                date=order_date(profile),
                category=random.choice(CATEGORIES),
            )
        )
        order_id += 1

    return orders


def update_customer_rollups(customers: list[Customer], orders: list[Order]) -> None:
    totals: dict[int, dict[str, object]] = defaultdict(
        lambda: {"total_orders": 0, "total_spent": Decimal("0.00"), "last_purchase_date": None}
    )

    for order in orders:
        summary = totals[order.customer_id]
        summary["total_orders"] = int(summary["total_orders"]) + 1
        summary["total_spent"] = Decimal(summary["total_spent"]) + order.amount
        current_last_purchase = summary["last_purchase_date"]
        if current_last_purchase is None or order.date > current_last_purchase:
            summary["last_purchase_date"] = order.date

    for customer in customers:
        summary = totals[customer.customer_id]
        customer.total_orders = int(summary["total_orders"])
        customer.total_spent = Decimal(summary["total_spent"]).quantize(Decimal("0.01"))
        customer.last_purchase_date = summary["last_purchase_date"]
        customer.loyalty_tier = loyalty_tier(
            customer.total_orders,
            customer.total_spent,
            customer.last_purchase_date,
        )


def write_customer_scores_snapshot(customers: list[Customer]) -> None:
    path = "data/customer_scores_snapshot.csv"
    with open(path, "w", encoding="utf-8") as file:
        file.write(
            "customer_id,name,email,total_orders,total_spent,last_purchase_date,"
            "preferred_channel,loyalty_tier,engagement_score\n"
        )
        for customer in customers:
            score = engagement_score(
                total_orders=customer.total_orders,
                total_spent=customer.total_spent,
                last_purchase_date=customer.last_purchase_date,
                preferred_channel_value=customer.preferred_channel,
            )
            file.write(
                f"{customer.customer_id},"
                f"\"{customer.name}\","
                f"{customer.email},"
                f"{customer.total_orders},"
                f"{customer.total_spent},"
                f"{customer.last_purchase_date or ''},"
                f"{customer.preferred_channel},"
                f"{customer.loyalty_tier},"
                f"{score}\n"
            )


def create_reference_data() -> tuple[list[Campaign], list[Segment]]:
    campaigns = [
        Campaign(
            name="Spring Winback",
            channel="email",
            status="draft",
            objective="Re-engage inactive customers with personalized offers.",
        ),
        Campaign(
            name="VIP Early Access",
            channel="whatsapp",
            status="draft",
            objective="Reward loyal customers with early product access.",
        ),
        Campaign(
            name="Cart Recovery Push",
            channel="push",
            status="draft",
            objective="Recover high-intent shoppers through reminders.",
        ),
    ]
    segments = [
        Segment(
            name="Inactive Customers",
            description="Customers with no recent purchases.",
            criteria_json='{"inactive_days_gt": 180}',
        ),
        Segment(
            name="Loyal High Spenders",
            description="Customers with strong order frequency or high total spend.",
            criteria_json='{"loyalty_tier_in": ["Gold", "Platinum"]}',
        ),
        Segment(
            name="Mobile Preferred",
            description="Customers who prefer SMS, WhatsApp, or push channels.",
            criteria_json='{"preferred_channel_in": ["sms", "whatsapp", "push"]}',
        ),
    ]
    return campaigns, segments


def seed() -> None:
    random.seed(42)
    Faker.seed(42)

    drop_database()
    create_database()

    customers, profiles = create_customers()
    orders = create_orders(profiles)
    update_customer_rollups(customers, orders)
    write_customer_scores_snapshot(customers)
    campaigns, segments = create_reference_data()

    with SessionLocal() as db:
        db.add_all(customers)
        db.flush()
        db.add_all(orders)
        db.add_all(campaigns)
        db.add_all(segments)
        db.commit()

        customer_count = db.scalar(select(func.count()).select_from(Customer))
        order_count = db.scalar(select(func.count()).select_from(Order))

    print(f"Seeded {customer_count} customers and {order_count} orders.")


if __name__ == "__main__":
    seed()
