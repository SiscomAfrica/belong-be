from __future__ import annotations

from apps.ai_profiler.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    API_KEY_SETTING = "GROQ_API_KEY"
    MODEL_SETTING = "GROQ_MODEL"
    DEFAULT_MODEL = "openai/gpt-oss-120b"
