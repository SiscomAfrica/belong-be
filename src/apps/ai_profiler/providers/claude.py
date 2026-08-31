from __future__ import annotations

import json

import httpx
from django.conf import settings

from apps.ai_profiler.providers.base import LLMProvider

DEFAULT_MODEL = "claude-sonnet-5"


class ClaudeProvider(LLMProvider):
    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": settings.ANTHROPIC_API_KEY,
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json",
        }

    def _model(self) -> str:
        return getattr(settings, "ANTHROPIC_MODEL", DEFAULT_MODEL)

    def _post(self, *, payload: dict, timeout: int) -> dict:
        resp = httpx.post(
            self.API_URL, json=payload, headers=self._headers(), timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def complete(self, *, messages: list[dict], system_prompt: str) -> str:
        data = self._post(
            payload={
                "model": self._model(),
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": messages,
            },
            timeout=60,
        )
        return data["content"][0]["text"]

    def complete_structured(
        self,
        *,
        messages: list[dict],
        system_prompt: str,
        schema: dict,
        timeout: int = 20,
    ) -> dict:
        data = self._post(
            payload={
                "model": self._model(),
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": messages,
                "output_config": {
                    "format": {"type": "json_schema", "schema": schema},
                },
            },
            timeout=timeout,
        )
        return json.loads(_first_text_block(data))


def _first_text_block(data: dict) -> str:
    for block in data.get("content", []):
        if block.get("type") == "text":
            return block["text"]
    msg = "Claude returned no text block for a structured request"
    raise ValueError(msg)
