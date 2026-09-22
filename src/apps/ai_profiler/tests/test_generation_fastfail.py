from __future__ import annotations

from unittest.mock import patch

from django.test import override_settings

from apps.ai_profiler.providers.claude import ClaudeProvider
from apps.ai_profiler.services.generate_question import generate_question


@override_settings(LLM_PROVIDER="claude", ANTHROPIC_API_KEY="")
def test_no_api_key_means_no_http_call_at_all() -> None:
    """An unset credential used to cost three round-trips that could only
    401 — generate, retry, retry — about 1.5s per question, paid by the user
    for a call that never had a chance of working.
    """
    with patch(
        "apps.ai_profiler.providers.claude.httpx.post",
    ) as post:
        question = generate_question(behaviour="motivation", asked=[])

    assert post.call_count == 0
    assert question["source"] == "fallback"


@override_settings(LLM_PROVIDER="claude", ANTHROPIC_API_KEY="")
def test_the_user_still_gets_a_usable_question() -> None:
    """Falling back must never mean falling over: the banked question is a
    real one, graded on the same anchors as a generated one.
    """
    question = generate_question(behaviour="motivation", asked=[])

    assert question["question"]
    assert len(question["options"]) >= 3


@override_settings(ANTHROPIC_API_KEY="")
def test_is_configured_reports_a_missing_key() -> None:
    assert ClaudeProvider().is_configured() is False


@override_settings(ANTHROPIC_API_KEY="sk-ant-something")
def test_is_configured_reports_a_present_key() -> None:
    assert ClaudeProvider().is_configured() is True
