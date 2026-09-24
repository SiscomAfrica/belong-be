from __future__ import annotations

from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.test import override_settings

from apps.ai_profiler.exceptions import ProviderRateLimitedError
from apps.ai_profiler.services.generate_question import generate_question
from apps.ai_profiler.services.provider_cooldown import (
    COOLDOWN_KEY,
    provider_is_cooling_down,
)
from apps.ai_profiler.tasks.refill_question_pool import refill_question_pool

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _clear_cooldown():
    cache.delete(COOLDOWN_KEY)
    yield
    cache.delete(COOLDOWN_KEY)


@override_settings(LLM_PROVIDER="groq", GROQ_API_KEY="gsk-configured")
def test_a_rate_limit_is_not_retried() -> None:
    """Three immediate attempts against a rate limiter only confirm it.

    Each refused call still costs a round trip, and the pool refill was making
    ninety of them per run.
    """
    with patch(
        "apps.ai_profiler.providers.openai_compatible.httpx.post",
    ) as post:
        post.return_value.status_code = 429
        post.return_value.headers = {}

        with pytest.raises(ProviderRateLimitedError):
            generate_question(behaviour="risk", asked=[])

    assert post.call_count == 1


@override_settings(LLM_PROVIDER="groq", GROQ_API_KEY="gsk-configured")
def test_the_refill_stops_at_the_first_refusal() -> None:
    """The limit is on the account, so the other behaviours would only meet
    the same answer. Six behaviours x five questions is thirty attempts.
    """
    with patch(
        "apps.ai_profiler.tasks.refill_question_pool.generate_question",
        side_effect=ProviderRateLimitedError(retry_after=None),
    ) as generate:
        created = refill_question_pool()

    assert created == 0
    assert generate.call_count == 1


@override_settings(LLM_PROVIDER="groq", GROQ_API_KEY="gsk-configured")
def test_a_refusal_starts_a_cooldown_that_skips_the_next_run() -> None:
    """Beat fires every five minutes; without this it walks straight back in."""
    with patch(
        "apps.ai_profiler.tasks.refill_question_pool.generate_question",
        side_effect=ProviderRateLimitedError(retry_after=None),
    ):
        refill_question_pool()

    assert provider_is_cooling_down()

    with patch(
        "apps.ai_profiler.tasks.refill_question_pool.generate_question",
    ) as generate:
        assert refill_question_pool() == 0

    assert generate.call_count == 0


@override_settings(LLM_PROVIDER="groq", GROQ_API_KEY="gsk-configured")
def test_retry_after_sets_how_long_to_wait() -> None:
    """The provider knows when its window reopens; we are guessing."""
    with patch(
        "apps.ai_profiler.providers.openai_compatible.httpx.post",
    ) as post:
        post.return_value.status_code = 429
        post.return_value.headers = {"Retry-After": "42"}

        with pytest.raises(ProviderRateLimitedError) as caught:
            generate_question(behaviour="risk", asked=[])

    assert caught.value.retry_after == 42
