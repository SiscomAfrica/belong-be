from __future__ import annotations

from unittest.mock import patch

import pytest

from apps.ai_profiler.models import PooledQuestion
from apps.ai_profiler.services.pooled_payload import pooled_payload

pytestmark = pytest.mark.django_db


def make_pooled(behaviour: str = "risk") -> PooledQuestion:
    return PooledQuestion.objects.create(
        behaviour=behaviour,
        prompt="A pooled question",
        subtitle="From the pool",
        options=[{"label": "a", "sublabel": "", "anchors": []}],
        secondary_behaviours=["mindset"],
    )


def test_a_pooled_question_is_served_without_calling_the_llm() -> None:
    """The whole point: generation is an LLM round-trip, and it must not sit
    between tapping Continue and seeing the next question.
    """
    make_pooled("risk")

    with patch(
        "apps.ai_profiler.services.generate_question.generate_question",
    ) as generate:
        payload = pooled_payload(behaviour="risk")

    assert payload is not None
    assert payload["question"] == "A pooled question"
    assert generate.call_count == 0


def test_a_question_is_served_to_exactly_one_session() -> None:
    """Two people answering at once must not be handed the same question."""
    make_pooled("risk")

    first = pooled_payload(behaviour="risk")
    second = pooled_payload(behaviour="risk")

    assert first is not None
    assert second is None


def test_claiming_marks_rather_than_deletes() -> None:
    """A question that turned out badly still has to be traceable from the
    session that served it.
    """
    pooled = make_pooled("horizon")

    pooled_payload(behaviour="horizon")
    pooled.refresh_from_db()

    assert pooled.claimed_at is not None


def test_an_empty_pool_reports_nothing_rather_than_raising() -> None:
    """next_question falls through to live generation on None; an exception
    here would take the whole session down instead.
    """
    assert pooled_payload(behaviour="market") is None


def test_the_payload_matches_what_generate_question_returns() -> None:
    """next_question treats pooled and freshly-generated questions
    identically, so the shapes cannot drift apart.
    """
    make_pooled("mindset")

    payload = pooled_payload(behaviour="mindset")

    assert payload is not None
    assert set(payload) == {
        "primary_behaviour",
        "secondary_behaviours",
        "question",
        "subtitle",
        "options",
        "source",
    }
