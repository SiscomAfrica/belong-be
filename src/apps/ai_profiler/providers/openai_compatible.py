from __future__ import annotations

import json

import httpx
from django.conf import settings

from apps.ai_profiler.exceptions import ProviderRateLimitedError
from apps.ai_profiler.providers.base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """Shared implementation for the /chat/completions request shape.

    Groq and OpenAI speak the same protocol, so they differ only in endpoint
    and which settings hold the key and model name.
    """

    API_URL: str = ""
    API_KEY_SETTING: str = ""
    MODEL_SETTING: str = ""
    DEFAULT_MODEL: str = ""
    SCHEMA_NAME: str = "generated_question"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {getattr(settings, self.API_KEY_SETTING, '')}",
            "Content-Type": "application/json",
        }

    def _model(self) -> str:
        return getattr(settings, self.MODEL_SETTING, self.DEFAULT_MODEL)

    def _post(self, *, payload: dict, timeout: int) -> dict:
        resp = httpx.post(
            self.API_URL, json=payload, headers=self._headers(), timeout=timeout,
        )
        if resp.status_code == httpx.codes.TOO_MANY_REQUESTS:
            # Raised as its own type so callers can stop rather than retry.
            # Honour Retry-After when the provider sends one; it knows when
            # the window reopens and we do not.
            raise ProviderRateLimitedError(retry_after=_retry_after(resp))
        resp.raise_for_status()
        return resp.json()

    def complete(self, *, messages: list[dict], system_prompt: str) -> str:
        data = self._post(
            payload={
                "model": self._model(),
                "messages": [{"role": "system", "content": system_prompt}, *messages],
                "max_tokens": 1024,
            },
            timeout=60,
        )
        return data["choices"][0]["message"]["content"]

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
                "messages": [{"role": "system", "content": system_prompt}, *messages],
                "max_tokens": 1024,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": self.SCHEMA_NAME,
                        "strict": True,
                        "schema": schema,
                    },
                },
            },
            timeout=timeout,
        )
        return json.loads(data["choices"][0]["message"]["content"])


def _retry_after(resp: httpx.Response) -> int | None:
    raw = resp.headers.get("Retry-After") or resp.headers.get("retry-after")
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        # Retry-After may be an HTTP date rather than seconds. Falling back to
        # the caller's own cooldown is better than guessing at a parse.
        return None
