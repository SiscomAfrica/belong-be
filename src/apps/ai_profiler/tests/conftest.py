from __future__ import annotations

import pytest

from apps.ai_profiler.models import ConversationSession, ProfileTemplate
from apps.ai_profiler.rubric import CENTROIDS
from apps.ai_profiler.services.record_answer import record_answer
from apps.users.models import User


@pytest.fixture
def no_llm(monkeypatch) -> None:
    """Force the fallback path so flows are exercised without a network call."""
    def unavailable(*args, **kwargs):
        msg = "no provider in tests"
        raise RuntimeError(msg)

    monkeypatch.setattr(
        "apps.ai_profiler.services.generate_question.get_llm_provider", unavailable,
    )


@pytest.fixture
def templates() -> list[ProfileTemplate]:
    return [
        ProfileTemplate.objects.create(
            investor_type=investor_type,
            name=investor_type.title(),
            slug=investor_type.lower(),
            badge_label=f"{investor_type} UNLOCK",
            description="A profile used in tests.",
            centroid=centroid,
            position=position,
        )
        for position, (investor_type, centroid) in enumerate(CENTROIDS.items())
    ]


@pytest.fixture
def user() -> User:
    return User.objects.create(
        phone="+254700000001", username="u1", referral_code="TESTUSER1",
    )


@pytest.fixture
def other_user() -> User:
    return User.objects.create(
        phone="+254700000002", username="u2", referral_code="TESTUSER2",
    )


@pytest.fixture
def session(user: User) -> ConversationSession:
    return ConversationSession.objects.create(user=user)


@pytest.fixture
def answer_first():
    """Answer a question with its first option."""
    def _answer(question) -> None:
        record_answer(
            question_id=question.id,
            user_id=question.session.user_id,
            selected_indexes=[0],
        )

    return _answer
