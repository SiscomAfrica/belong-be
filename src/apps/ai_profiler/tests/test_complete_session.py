from __future__ import annotations

import pytest

from apps.ai_profiler.models import ConversationMessage, MessageRole, SessionStatus
from apps.ai_profiler.models.investor_profile import ScoringMethod
from apps.ai_profiler.services.complete_session import complete_session
from apps.ai_profiler.services.next_question import next_question

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("no_llm", "templates"),
]


def answer_everything(session, answer_first) -> None:
    while question := next_question(session_id=session.id, user_id=session.user_id):
        answer_first(question)


def test_a_generated_session_is_scored_by_the_rubric(session, answer_first) -> None:
    answer_everything(session, answer_first)
    profile = complete_session(session_id=session.id, user_id=session.user_id)

    assert profile.scoring_method == ScoringMethod.RUBRIC
    assert profile.behaviour_vector


def test_a_legacy_session_is_not_scored_by_the_rubric(session) -> None:
    """An old client posts a text blob and creates no questions.

    Scoring it with the rubric would impute every behaviour to the median and
    hand every such user the same profile.
    """
    ConversationMessage.objects.create(
        session=session,
        role=MessageRole.USER,
        content="I want long term growth and I am comfortable with high risk.",
    )

    profile = complete_session(session_id=session.id, user_id=session.user_id)

    assert profile.scoring_method == ScoringMethod.LEGACY
    assert profile.behaviour_vector == {}


def test_legacy_scoring_still_varies_with_the_answer(session, other_user) -> None:
    """The old path was flawed, but it was not uniform. It must stay non-uniform."""
    from apps.ai_profiler.models import ConversationSession

    ConversationMessage.objects.create(
        session=session, role=MessageRole.USER,
        content="I want to preserve my capital, keep it safe.",
    )
    cautious = complete_session(session_id=session.id, user_id=session.user_id)

    bold_session = ConversationSession.objects.create(user=other_user)
    ConversationMessage.objects.create(
        session=bold_session, role=MessageRole.USER,
        content="I want maximum returns, high risk is fine.",
    )
    bold = complete_session(session_id=bold_session.id, user_id=other_user.id)

    assert cautious.risk_tolerance != bold.risk_tolerance


def test_legacy_profiles_are_findable_for_re_profiling(session) -> None:
    from apps.ai_profiler.models import InvestorProfile

    ConversationMessage.objects.create(
        session=session, role=MessageRole.USER, content="steady growth please",
    )
    complete_session(session_id=session.id, user_id=session.user_id)

    assert InvestorProfile.objects.filter(
        scoring_method=ScoringMethod.LEGACY,
    ).count() == 1


def test_both_paths_close_the_session(session) -> None:
    ConversationMessage.objects.create(
        session=session, role=MessageRole.USER, content="balanced approach",
    )
    complete_session(session_id=session.id, user_id=session.user_id)
    session.refresh_from_db()

    assert session.status == SessionStatus.COMPLETED
    assert session.summary
