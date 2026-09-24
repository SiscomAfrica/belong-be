from __future__ import annotations

from django.core.cache import cache

# Beat fires the pool refill every five minutes. Without a cooldown, a
# provider that is refusing calls was met with ninety more of them per tick —
# six behaviours, five questions each, three attempts apiece — for a run that
# created nothing and took twenty seconds. The refusal is on the account, so
# one behaviour hitting it means all of them would.
COOLDOWN_KEY = "ai_profiler:provider_cooldown"
DEFAULT_COOLDOWN_SECONDS = 15 * 60


def provider_is_cooling_down() -> bool:
    return bool(cache.get(COOLDOWN_KEY))


def start_provider_cooldown(*, seconds: int | None = None) -> None:
    """Stop calling the provider for a while.

    Prefers the provider's own Retry-After when it sent one — it knows when
    the window reopens and we are guessing.
    """
    cache.set(COOLDOWN_KEY, True, timeout=seconds or DEFAULT_COOLDOWN_SECONDS)


def clear_provider_cooldown() -> None:
    cache.delete(COOLDOWN_KEY)
