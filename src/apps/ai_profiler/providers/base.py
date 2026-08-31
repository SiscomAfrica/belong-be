from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
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
