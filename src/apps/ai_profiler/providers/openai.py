from __future__ import annotations

import httpx
from django.conf import settings

from apps.ai_profiler.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    API_URL = "https://api.openai.com/v1/chat/completions"

    def complete(self, *, messages: list[dict], system_prompt: str) -> str:
        api_key = settings.OPENAI_API_KEY
        model = getattr(settings, "OPENAI_MODEL", "gpt-4o")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        full_messages = [{"role": "system", "content": system_prompt}, *messages]
        payload = {"model": model, "messages": full_messages, "max_tokens": 1024}
        resp = httpx.post(self.API_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
