from __future__ import annotations

from z3phyr.config import Settings
from z3phyr.llm.gemini import GeminiProvider
from z3phyr.llm.mock import MockProvider
from z3phyr.llm.openai_compat import OpenAICompatProvider


def build_provider(settings: Settings, *, force_provider: str | None = None):
    provider_name = (force_provider or settings.provider).strip().lower()
    if provider_name == "mock":
        return MockProvider()
    if provider_name == "gemini":
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY is required when provider is gemini. "
                "Use --provider mock for offline dry-runs."
            )
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.model)
    if provider_name in {"openai", "openai_compat"}:
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when provider is openai/openai_compat."
            )
        return OpenAICompatProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.model,
        )
    raise ValueError(f"Unsupported provider: {provider_name}")
