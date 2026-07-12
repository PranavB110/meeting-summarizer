"""Picks the LLM provider based on config — config-switchable summarization."""
from app.core.config import Settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.groq_provider import GroqProvider


def get_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("LLM_PROVIDER=groq requires GROQ_API_KEY to be set")
        return GroqProvider(api_key=settings.groq_api_key, model=settings.groq_model)

    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")