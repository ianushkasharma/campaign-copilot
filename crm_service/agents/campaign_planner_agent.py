import json
import logging

from crm_service.agents.audience_agent import AudienceAgent
from crm_service.agents.prompts import CAMPAIGN_PLANNER_PROMPT
from shared.gemini import GeminiClient, GeminiClientUnavailableError

logger = logging.getLogger(__name__)


class CampaignPlannerAgent:
    def __init__(self) -> None:
        self.audience_agent = AudienceAgent()

    def plan_campaign(
        self,
        goal: str,
        audience_filters: dict[str, object],
        audience_size: int,
        audience_reasoning: str,
    ) -> dict[str, object]:
        try:
            plan = self._plan_with_gemini(goal, audience_filters, audience_size, audience_reasoning)
        except GeminiClientUnavailableError:
            logger.exception("CampaignPlannerAgent Gemini path failed. Falling back to rules.")
            plan = self._fallback_plan(goal, audience_filters, audience_size, audience_reasoning)
        except (json.JSONDecodeError, ValueError, TypeError):
            logger.exception("CampaignPlannerAgent could not parse Gemini response. Falling back to rules.")
            plan = self._fallback_plan(goal, audience_filters, audience_size, audience_reasoning)
        except Exception:
            logger.exception("CampaignPlannerAgent unexpected AI failure. Falling back to rules.")
            plan = self._fallback_plan(goal, audience_filters, audience_size, audience_reasoning)

        return self._normalize_plan(plan, goal, audience_filters, audience_size, audience_reasoning)

    def build_audience_filters(self, goal: str) -> dict[str, object]:
        return self.audience_agent.build_filters(goal)

    def _plan_with_gemini(
        self,
        goal: str,
        audience_filters: dict[str, object],
        audience_size: int,
        audience_reasoning: str,
    ) -> dict[str, object]:
        prompt = (
            CAMPAIGN_PLANNER_PROMPT
            .replace("{goal}", goal)
            .replace("{filters_json}", json.dumps(audience_filters))
            .replace("{audience_size}", str(audience_size))
            .replace("{audience_reasoning}", audience_reasoning)
        )
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

    def _fallback_plan(
        self,
        goal: str,
        audience_filters: dict[str, object],
        audience_size: int,
        audience_reasoning: str,
    ) -> dict[str, object]:
        is_winback = any(term in goal.lower() for term in ["inactive", "bring back", "win back", "re-engage"])
        channel = "whatsapp" if is_winback else "email"
        open_rate = 0.70 if channel == "whatsapp" else 0.35
        click_rate = 0.18 if is_winback else 0.12
        purchase_rate = 0.045 if is_winback else 0.03
        estimated_purchases = round(audience_size * purchase_rate)

        return {
            "goal_understanding": "Re-engage inactive customers and motivate them to make another purchase.",
            "recommended_audience": {
                "name": "Inactive Winback Audience",
                "filters": audience_filters,
                "description": "Customers who have not purchased recently and are suitable for a reactivation offer.",
            },
            "audience_reasoning": audience_reasoning,
            "recommended_channel": {
                "channel": channel,
                "rationale": "This channel is strong for direct reactivation messages and quick customer response.",
            },
            "recommended_offer": {
                "offer_type": "limited_time_discount",
                "offer_value": "15% off the next order",
                "rationale": "A clear, time-bound incentive reduces friction for lapsed customers.",
            },
            "personalized_message": {
                "subject": "We saved something special for you",
                "body": (
                    "Hi {name}, we miss you. Come back this week and get 15% off your next order. "
                    "Your favorites are waiting."
                ),
            },
            "expected_performance": {
                "audience_size": audience_size,
                "estimated_delivery_rate": 0.92,
                "estimated_open_rate": open_rate,
                "estimated_click_rate": click_rate,
                "estimated_purchase_rate": purchase_rate,
                "estimated_purchases": estimated_purchases,
                "estimated_revenue": round(estimated_purchases * 75.0, 2),
                "rationale": "Winback campaigns usually see moderate engagement and lower purchase rates than active customer campaigns.",
            },
        }

    def _normalize_plan(
        self,
        plan: dict[str, object],
        goal: str,
        audience_filters: dict[str, object],
        audience_size: int,
        audience_reasoning: str,
    ) -> dict[str, object]:
        fallback = self._fallback_plan(goal, audience_filters, audience_size, audience_reasoning)
        normalized = fallback | {key: value for key, value in plan.items() if value not in (None, "", [], {})}

        recommended_audience = normalized.get("recommended_audience")
        if not isinstance(recommended_audience, dict):
            normalized["recommended_audience"] = fallback["recommended_audience"]
        else:
            recommended_audience.setdefault("filters", audience_filters)

        expected_performance = normalized.get("expected_performance")
        if not isinstance(expected_performance, dict):
            normalized["expected_performance"] = fallback["expected_performance"]
        else:
            expected_performance["audience_size"] = audience_size

        return normalized
