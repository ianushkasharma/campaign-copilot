from shared.config import settings


def get_gemini_settings() -> dict[str, str]:
    return {
        "api_key": settings.gemini_api_key,
        "model": settings.gemini_model,
    }
