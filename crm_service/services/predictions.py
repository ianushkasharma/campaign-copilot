import re

from crm_service.schemas import (
    AudienceCharacteristics,
    CampaignPredictionRequest,
    CampaignPredictionResponse,
    OfferInput,
)


class CampaignPredictionEngine:
    CHANNEL_BASELINES = {
        "whatsapp": {"open": 0.70, "click": 0.18, "conversion": 0.045},
        "sms": {"open": 0.50, "click": 0.12, "conversion": 0.035},
        "email": {"open": 0.35, "click": 0.09, "conversion": 0.028},
        "push": {"open": 0.45, "click": 0.10, "conversion": 0.030},
        "phone": {"open": 0.30, "click": 0.08, "conversion": 0.025},
    }

    DEFAULT_AVERAGE_ORDER_VALUE = 75.0

    def predict(self, data: CampaignPredictionRequest) -> CampaignPredictionResponse:
        channel = data.channel.lower()
        baseline = self.CHANNEL_BASELINES.get(channel, self.CHANNEL_BASELINES["email"])
        assumptions = [f"Used {channel} channel baseline rates."]

        open_rate = baseline["open"]
        click_rate = baseline["click"]
        conversion_rate = baseline["conversion"]

        audience_modifier, audience_notes = self._audience_modifier(data.audience, channel)
        offer_modifier, offer_notes = self._offer_modifier(data.offer)

        open_rate *= audience_modifier["open"]
        click_rate *= audience_modifier["click"] * offer_modifier["click"]
        conversion_rate *= audience_modifier["conversion"] * offer_modifier["conversion"]

        assumptions.extend(audience_notes)
        assumptions.extend(offer_notes)

        avg_order_value = self._average_order_value(data.audience, data.offer)
        predicted_revenue = data.audience.audience_size * conversion_rate * avg_order_value
        assumptions.append(f"Revenue uses estimated average order value of {avg_order_value:.2f}.")

        return CampaignPredictionResponse(
            predicted_open_rate=self._rate(open_rate),
            predicted_click_rate=self._rate(click_rate),
            predicted_conversion_rate=self._rate(conversion_rate),
            predicted_revenue=round(predicted_revenue, 2),
            assumptions=assumptions,
        )

    def _audience_modifier(
        self,
        audience: AudienceCharacteristics,
        channel: str,
    ) -> tuple[dict[str, float], list[str]]:
        modifier = {"open": 1.0, "click": 1.0, "conversion": 1.0}
        notes: list[str] = []

        inactive_days = audience.inactive_days_gt
        if inactive_days is None and audience.filters:
            raw_inactive_days = audience.filters.get("inactive_days_gt")
            if isinstance(raw_inactive_days, int):
                inactive_days = raw_inactive_days

        if inactive_days:
            modifier["open"] *= 0.90
            modifier["click"] *= 0.88
            modifier["conversion"] *= 0.82
            notes.append("Inactive audiences are discounted for lower engagement and conversion.")

        if audience.avg_total_spent and audience.avg_total_spent >= 5000:
            modifier["conversion"] *= 1.20
            notes.append("High historical spend increases conversion likelihood.")

        if audience.avg_total_orders and audience.avg_total_orders >= 5:
            modifier["click"] *= 1.08
            modifier["conversion"] *= 1.10
            notes.append("Repeat purchase history improves click and conversion rates.")

        if audience.preferred_channel_mix:
            aligned_share = audience.preferred_channel_mix.get(channel, 0)
            if aligned_share >= 0.4:
                modifier["open"] *= 1.10
                modifier["click"] *= 1.05
                notes.append("A large share of the audience prefers the selected channel.")

        if audience.loyalty_tier_mix:
            loyal_share = audience.loyalty_tier_mix.get("Gold", 0) + audience.loyalty_tier_mix.get("Platinum", 0)
            if loyal_share >= 0.25:
                modifier["conversion"] *= 1.15
                notes.append("Gold and Platinum customers increase purchase propensity.")

        return modifier, notes

    def _offer_modifier(self, offer: OfferInput) -> tuple[dict[str, float], list[str]]:
        modifier = {"click": 1.0, "conversion": 1.0}
        notes: list[str] = []
        offer_text = f"{offer.offer_type} {offer.offer_value}".lower()

        if any(term in offer_text for term in ["discount", "% off", "off", "coupon"]):
            modifier["click"] *= 1.10
            modifier["conversion"] *= 1.18
            notes.append("Discount incentives increase click and purchase likelihood.")

        discount = self._extract_discount_percent(offer_text)
        if discount:
            if discount >= 20:
                modifier["click"] *= 1.08
                modifier["conversion"] *= 1.12
                notes.append("A strong discount creates additional urgency.")
            elif discount < 10:
                modifier["conversion"] *= 0.92
                notes.append("A small discount may be less motivating.")

        if any(term in offer_text for term in ["free shipping", "free delivery"]):
            modifier["conversion"] *= 1.08
            notes.append("Free shipping reduces purchase friction.")

        if any(term in offer_text for term in ["limited", "today", "48 hour", "this week"]):
            modifier["click"] *= 1.06
            notes.append("Time-bound offers add urgency.")

        return modifier, notes

    def _average_order_value(self, audience: AudienceCharacteristics, offer: OfferInput) -> float:
        if audience.avg_total_spent and audience.avg_total_orders and audience.avg_total_orders > 0:
            average_order_value = audience.avg_total_spent / audience.avg_total_orders
        else:
            average_order_value = self.DEFAULT_AVERAGE_ORDER_VALUE

        discount = self._extract_discount_percent(f"{offer.offer_type} {offer.offer_value}".lower())
        if discount:
            average_order_value *= max(0.5, 1 - (discount / 100))

        return round(max(average_order_value, 10), 2)

    def _extract_discount_percent(self, text: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
        if not match:
            return None
        return float(match.group(1))

    def _rate(self, value: float) -> float:
        return round(min(max(value, 0.0), 0.95), 4)


class CampaignPredictionService:
    def __init__(self) -> None:
        self.engine = CampaignPredictionEngine()

    def predict(self, data: CampaignPredictionRequest) -> CampaignPredictionResponse:
        return self.engine.predict(data)
