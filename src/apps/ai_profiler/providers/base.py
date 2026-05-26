from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, *, messages: list[dict], system_prompt: str) -> str:
        ...
