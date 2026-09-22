from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    #: Settings attribute holding this provider's credential.
    api_key_setting: str = ""

    def is_configured(self) -> bool:
        """Whether calling this provider could possibly succeed.

        Without it, an unset key costs three HTTP round-trips that can only
        ever 401 — generate, retry, retry — before the banked fallback is
        served. Measured at ~1.5s per question, paid by the user, for nothing.
        """
        from django.conf import settings

        return bool(getattr(settings, self.api_key_setting, ""))

    @abstractmethod
    def complete(self, *, messages: list[dict], system_prompt: str) -> str:
        """Free-text completion. Used for conversational replies."""
        ...

    @abstractmethod
    def complete_structured(
        self,
        *,
        messages: list[dict],
        system_prompt: str,
        schema: dict,
        timeout: int = 20,
    ) -> dict:
        """Completion constrained to `schema`, returned as parsed JSON.

        Question generation depends on the response shape being guaranteed
        rather than parsed hopefully — a malformed question is not something
        we can recover from mid-onboarding.
        """
        ...
