import json
import logging

from crm_service.agents.prompts import SEGMENT_NAMING_PROMPT
from shared.gemini import GeminiClient, GeminiClientUnavailableError

logger = logging.getLogger(__name__)


class SegmentNamingAgent:
    def name_segment(self, segment_facts: dict[str, object]) -> dict[str, str]:
        try:
            prompt = SEGMENT_NAMING_PROMPT.replace("{segment_facts_json}", json.dumps(segment_facts, default=str))
            text = GeminiClient().generate_text(prompt)
            parsed = self._json_from_text(text)
        except (GeminiClientUnavailableError, json.JSONDecodeError, ValueError, TypeError):
            logger.exception("SegmentNamingAgent Gemini path failed. Falling back to rules.")
            parsed = self._fallback_name(segment_facts)
        except Exception:
            logger.exception("SegmentNamingAgent unexpected AI failure. Falling back to rules.")
            parsed = self._fallback_name(segment_facts)

        return {
            "segment_name": str(parsed.get("segment_name") or self._fallback_name(segment_facts)["segment_name"]),
            "description": str(parsed.get("description") or self._fallback_name(segment_facts)["description"]),
        }

    def _json_from_text(self, text: str) -> dict[str, object]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").replace("json", "", 1).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object found.")
        return json.loads(cleaned[start : end + 1])

    def _fallback_name(self, segment_facts: dict[str, object]) -> dict[str, str]:
        tier = str(segment_facts.get("loyalty_tier") or "Customer")
        conversion_rate = float(segment_facts.get("conversion_rate") or 0)
        if conversion_rate >= 0.08:
            label = f"{tier} Growth Champions"
            description = "High-performing customers who are strong candidates for scaling."
        elif conversion_rate >= 0.03:
            label = f"{tier} Persuadables"
            description = "Customers showing moderate response and room for offer optimization."
        else:
            label = f"{tier} Recovery Audience"
            description = "Customers needing stronger reactivation messaging or a different channel."
        return {"segment_name": label, "description": description}
