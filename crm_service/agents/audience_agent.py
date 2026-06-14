import json
import logging
import re
from decimal import Decimal

from crm_service.agents.prompts import AUDIENCE_SEGMENTATION_PROMPT
from shared.gemini import GeminiClient, GeminiClientUnavailableError

logger = logging.getLogger(__name__)


class AudienceAgent:
    def __init__(self) -> None:
        self.allowed_filter_keys = {
            "inactive_days_gt",
            "total_spent_gt",
            "total_spent_gte",
            "total_spent_lt",
            "total_orders_gt",
            "total_orders_gte",
            "loyalty_tier_in",
            "city",
            "gender",
            "preferred_channel_in",
        }

    def build_filters(self, query: str) -> dict[str, object]:
        try:
            parsed = self._parse_with_gemini(query)
        except GeminiClientUnavailableError:
            logger.exception("AudienceAgent Gemini path failed. Falling back to rules.")
            parsed = self._parse_locally(query)
        except (json.JSONDecodeError, ValueError, TypeError):
            logger.exception("AudienceAgent could not parse Gemini response. Falling back to rules.")
            parsed = self._parse_locally(query)
        except Exception:
            logger.exception("AudienceAgent unexpected AI failure. Falling back to rules.")
            parsed = self._parse_locally(query)

        filters = self._sanitize_filters(parsed.get("filters", {}))
        reasoning = str(parsed.get("reasoning") or self._fallback_reasoning(filters))
        return {"filters": filters, "reasoning": reasoning}

    def build_fallback_filters(self, query: str) -> dict[str, object]:
        parsed = self._parse_locally(query)
        filters = self._sanitize_filters(parsed.get("filters", {}))
        reasoning = str(parsed.get("reasoning") or self._fallback_reasoning(filters))
        return {"filters": filters, "reasoning": reasoning}

    def _parse_with_gemini(self, query: str) -> dict[str, object]:
        prompt = AUDIENCE_SEGMENTATION_PROMPT.replace("{query}", query)
        text = GeminiClient().generate_text(prompt)
        return self._json_from_text(text)

    def _json_from_text(self, text: str) -> dict[str, object]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Gemini response did not contain a JSON object.")
        return json.loads(cleaned[start : end + 1])

    def _parse_locally(self, query: str) -> dict[str, object]:
        normalized = query.lower()
        filters: dict[str, object] = {}

        if "inactive" in normalized or "dormant" in normalized or "lapsed" in normalized:
            filters["inactive_days_gt"] = self._extract_days(normalized) or 180

        spent_value = self._extract_money_threshold(normalized)
        if spent_value is not None:
            if any(term in normalized for term in ["more than", "greater than", "above", "over", ">"]):
                filters["total_spent_gt"] = spent_value
            else:
                filters["total_spent_gte"] = spent_value
        elif any(term in normalized for term in ["high spend", "high-spend", "high value", "high-value", "big spender"]):
            filters["total_spent_gt"] = 5000

        orders_value = self._extract_order_threshold(normalized)
        if orders_value is not None:
            filters["total_orders_gte"] = orders_value

        channels = [channel for channel in ["email", "sms", "whatsapp", "push", "phone"] if channel in normalized]
        if channels:
            filters["preferred_channel_in"] = channels

        if any(term in normalized for term in ["loyal", "vip", "best customer", "best customers"]):
            filters["loyalty_tier_in"] = ["Gold", "Platinum"]

        tiers = [
            tier
            for tier in ["prospect", "bronze", "silver", "gold", "platinum"]
            if tier in normalized
        ]
        if tiers:
            existing_tiers = filters.get("loyalty_tier_in", [])
            if not isinstance(existing_tiers, list):
                existing_tiers = []
            filters["loyalty_tier_in"] = sorted({*existing_tiers, *[tier.title() for tier in tiers]})

        reasoning = self._fallback_reasoning(filters)
        return {"filters": filters, "reasoning": reasoning}

    def _sanitize_filters(self, raw_filters: object) -> dict[str, object]:
        if not isinstance(raw_filters, dict):
            return {}

        filters: dict[str, object] = {}
        for key, value in raw_filters.items():
            if key not in self.allowed_filter_keys or value in (None, "", []):
                continue
            if key.endswith("_in") and isinstance(value, list):
                filters[key] = [str(item) for item in value]
            elif key in {"city", "gender"}:
                filters[key] = str(value)
            elif key.startswith("total_spent"):
                filters[key] = float(Decimal(str(value)))
            elif key.startswith("total_orders") or key == "inactive_days_gt":
                filters[key] = int(value)
        return filters

    def _extract_money_threshold(self, query: str) -> float | None:
        patterns = [
            r"(?:spent|spend|spending|value|worth)[^\d]*(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)",
            r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)",
            r"(?:more than|greater than|above|over|>)\s*([\d,]+(?:\.\d+)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return float(match.group(1).replace(",", ""))
        return None

    def _extract_order_threshold(self, query: str) -> int | None:
        match = re.search(r"(?:orders?|purchases?)[^\d]*(\d+)", query)
        if match:
            return int(match.group(1))
        return None

    def _extract_days(self, query: str) -> int | None:
        match = re.search(r"(\d+)\s*(?:days?|d)", query)
        if match:
            return int(match.group(1))

        months = re.search(r"(\d+)\s*(?:months?|mo)", query)
        if months:
            return int(months.group(1)) * 30

        years = re.search(r"(\d+)\s*(?:years?|yr)", query)
        if years:
            return int(years.group(1)) * 365

        return None

    def _fallback_reasoning(self, filters: dict[str, object]) -> str:
        if not filters:
            return "No specific filters were detected, so the broad customer audience was selected."
        return "The audience was selected by converting the request into structured customer filters."
