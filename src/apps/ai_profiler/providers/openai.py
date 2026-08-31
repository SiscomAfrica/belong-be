from __future__ import annotations

from apps.ai_profiler.providers.openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    API_URL = "https://api.openai.com/v1/chat/completions"
    API_KEY_SETTING = "OPENAI_API_KEY"
    MODEL_SETTING = "OPENAI_MODEL"
    DEFAULT_MODEL = "gpt-4o"
