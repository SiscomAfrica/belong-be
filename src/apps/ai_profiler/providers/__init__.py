from __future__ import annotations

from django.conf import settings

from apps.ai_profiler.providers.base import LLMProvider
from apps.ai_profiler.providers.claude import ClaudeProvider
from apps.ai_profiler.providers.openai import OpenAIProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
}


def get_llm_provider() -> LLMProvider:
    name = getattr(settings, "LLM_PROVIDER", "claude")
    cls = _PROVIDERS.get(name)
    if cls is None:
        msg = f"Unknown LLM provider: {name}"
        raise ValueError(msg)
    return cls()
