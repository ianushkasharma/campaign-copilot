import logging

from shared.config import settings

logger = logging.getLogger(__name__)

AI_FALLBACK_MESSAGE = "AI service unavailable. Using rule-based audience segmentation."


class GeminiClientUnavailableError(Exception):
    pass


class GeminiClient:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise GeminiClientUnavailableError("GEMINI_API_KEY is not configured.")

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise GeminiClientUnavailableError("google-generativeai is not installed.") from exc

        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
        except Exception as exc:
            logger.exception("Gemini client initialization failed.")
            raise GeminiClientUnavailableError("Gemini client initialization failed.") from exc

    def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            text = getattr(response, "text", None)
            if not text:
                raise GeminiClientUnavailableError("Gemini returned an empty response.")
            return text
        except GeminiClientUnavailableError:
            logger.exception("Gemini returned an unusable response.")
            raise
        except Exception as exc:
            logger.exception("Gemini API request failed.")
            raise GeminiClientUnavailableError("Gemini API request failed.") from exc
