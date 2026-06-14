import json
import logging

from crm_service.agents.prompts import INSIGHTS_PROMPT
from shared.gemini import GeminiClient, GeminiClientUnavailableError

logger = logging.getLogger(__name__)


class InsightsAgent:
    def analyze(self, campaign_data: dict[str, object]) -> dict[str, object]:
        try:
            insights = self._analyze_with_gemini(campaign_data)
        except GeminiClientUnavailableError:
            logger.exception("InsightsAgent Gemini path failed. Falling back to rules.")
            insights = self._fallback_insights(campaign_data)
        except (json.JSONDecodeError, ValueError, TypeError):
            logger.exception("InsightsAgent could not parse Gemini response. Falling back to rules.")
            insights = self._fallback_insights(campaign_data)
        except Exception:
            logger.exception("InsightsAgent unexpected AI failure. Falling back to rules.")
            insights = self._fallback_insights(campaign_data)
        return self._normalize(insights, campaign_data)

    def _analyze_with_gemini(self, campaign_data: dict[str, object]) -> dict[str, object]:
        prompt = INSIGHTS_PROMPT.replace("{campaign_data_json}", json.dumps(campaign_data, default=str))
        text = GeminiClient().generate_text(prompt)
        return self._json_from_text(text)

    def _json_from_text(self, text: str) -> dict[str, object]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").replace("json", "", 1).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Gemini response did not contain JSON.")
        return json.loads(cleaned[start : end + 1])

    def _fallback_insights(self, campaign_data: dict[str, object]) -> dict[str, object]:
        summary = campaign_data.get("summary", {})
        if not isinstance(summary, dict):
            summary = {}

        messages_sent = int(summary.get("messages_sent", 0))
        delivered = int(summary.get("delivered", 0))
        opened = int(summary.get("opened", 0))
        clicked = int(summary.get("clicked", 0))
        purchased = int(summary.get("purchased", 0))
        failed = int(summary.get("failed", 0))
        revenue = float(campaign_data.get("revenue_generated", 0))
        best_segment = campaign_data.get("best_segment") or {"name": "Unknown", "reason": "No segment data available."}
        worst_segment = campaign_data.get("worst_segment") or {"name": "Unknown", "reason": "No segment data available."}
        best_channel = campaign_data.get("best_channel") or {"name": "Unknown", "reason": "No channel data available."}

        open_rate = opened / delivered if delivered else 0
        purchase_rate = purchased / messages_sent if messages_sent else 0

        return {
            "what_happened": (
                f"The campaign sent {messages_sent} messages, delivered {delivered}, "
                f"opened {opened}, clicked {clicked}, and generated {purchased} purchases."
            ),
            "why_it_happened": (
                "Performance was shaped by delivery quality, channel engagement, and audience fit. "
                f"The observed open rate was {open_rate:.1%} and purchase rate was {purchase_rate:.1%}."
            ),
            "best_segment": best_segment,
            "worst_segment": worst_segment,
            "best_channel": best_channel,
            "revenue_generated": revenue,
            "recommended_next_action": (
                "Scale the best-performing segment and channel while testing a revised offer for weaker segments."
                if messages_sent else
                "Send the campaign to an audience before running post-campaign analysis."
            ),
        }

    def _normalize(self, insights: dict[str, object], campaign_data: dict[str, object]) -> dict[str, object]:
        fallback = self._fallback_insights(campaign_data)
        normalized = fallback | {key: value for key, value in insights.items() if value not in (None, "", [], {})}
        for key in ["best_segment", "worst_segment", "best_channel"]:
            if not isinstance(normalized.get(key), dict):
                normalized[key] = fallback[key]
        normalized["revenue_generated"] = float(normalized.get("revenue_generated", 0))
        return normalized
