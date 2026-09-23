from __future__ import annotations

from unittest.mock import patch

import pytest
from django.test import override_settings

from apps.ai_profiler.models import PooledQuestion, QuestionSource
from apps.ai_profiler.services.next_question import next_question

pytestmark = pytest.mark.django_db


@override_settings(LLM_PROVIDER="claude", ANTHROPIC_API_KEY="sk-ant-configured")
def test_a_dry_pool_serves_the_bank_without_calling_the_llm(session) -> None:
    """The availability guarantee, stated as a test.

    A miss used to fall through to generate_question, which is up to
    LLM_GENERATION_RETRIES + 1 attempts at LLM_GENERATION_TIMEOUT each —
    longer than the mobile client waits before aborting, so the user saw a
    hang instead of a question. A credential is configured here precisely so
    that the old path would have made a real call.
    """
    assert not PooledQuestion.objects.exists()

    with patch(
        "apps.ai_profiler.services.generate_question.generate_question",
    ) as generate, patch(
        "apps.ai_profiler.providers.claude.httpx.post",
    ) as post:
        question = next_question(
            session_id=session.id, user_id=session.user_id,
        )

    assert generate.call_count == 0
    assert post.call_count == 0
    assert question is not None
    assert question.prompt
    assert question.source == QuestionSource.FALLBACK


@override_settings(LLM_PROVIDER="claude", ANTHROPIC_API_KEY="sk-ant-configured")
def test_a_dry_pool_asks_for_a_refill(session, django_capture_on_commit_callbacks) -> None:
    """Serving the bank is a stopgap: the pool has to heal for the next user.

    The refill is queued through transaction.on_commit, which never fires
    inside the transaction a django_db test rolls back — hence capturing the
    callbacks and executing them, rather than asserting on delay alone.
    """
    with patch(
        "apps.ai_profiler.tasks.refill_question_pool.refill_question_pool.delay",
    ) as delay, django_capture_on_commit_callbacks(execute=True):
        next_question(session_id=session.id, user_id=session.user_id)

    assert delay.call_count == 1


def test_a_warm_pool_is_still_preferred(session) -> None:
    """The bank is the floor, not the default — a pooled question still wins."""
    PooledQuestion.objects.create(
        behaviour="motivation",
        prompt="A pooled question",
        subtitle="",
        options=[{"label": "a", "sublabel": "", "anchors": []}],
        secondary_behaviours=[],
    )

    question = next_question(session_id=session.id, user_id=session.user_id)

    assert question is not None
    assert question.prompt == "A pooled question"
