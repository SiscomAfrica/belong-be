from __future__ import annotations

import httpx
from django.conf import settings

from apps.ai_profiler.providers.base import LLMProvider


class ClaudeProvider(LLMProvider):
    API_URL = "https://api.anthropic.com/v1/messages"

    def complete(self, *, messages: list[dict], system_prompt: str) -> str:
        api_key = settings.ANTHROPIC_API_KEY
        model = getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": messages,
        }
        resp = httpx.post(self.API_URL, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
