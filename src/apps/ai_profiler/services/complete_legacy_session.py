from __future__ import annotations

import logging
from uuid import UUID

from apps.ai_profiler.models import ConversationSession, InvestorProfile
from apps.ai_profiler.models.investor_profile import ScoringMethod
from apps.ai_profiler.services.finalise_profile import finalise_profile
from apps.ai_profiler.services.score_investor_type import score_investor_type

logger = logging.getLogger(__name__)


def complete_legacy_session(
    *, session: ConversationSession, user_id: UUID,
) -> InvestorProfile:
    """Score a session created by a client that predates question generation.

    Those clients post a single text blob and never create SessionQuestion
    rows, so the rubric has nothing to read. Scoring them with the rubric
    anyway would impute every behaviour to the median and assign every one of
    them the same profile — worse than the keyword scorer they were already
    getting. So they keep the old path exactly, and get marked LEGACY so the
    affected users can be found and re-profiled once the app has rolled out.
    """
    logger.warning(
        "Session %s has no generated questions; scoring via the legacy path",
        session.id,
    )

    scores = score_investor_type(messages=list(session.messages.all()))

    profile, _ = InvestorProfile.objects.update_or_create(
        user_id=user_id,
        defaults={
            "risk_tolerance": scores["risk_tolerance"],
            "time_horizon": scores["time_horizon"],
            "investment_goal": scores["investment_goal"],
            "interests": scores["interests"],
            "behaviour_vector": {},
            "imputed_behaviours": [],
            "scoring_method": ScoringMethod.LEGACY,
        },
    )

    return finalise_profile(
        session=session,
        user_id=user_id,
        profile=profile,
        investor_type=scores["investor_type"],
        summary=f"Legacy scoring — type: {scores['investor_type']}",
        audit_values={"scoring_method": ScoringMethod.LEGACY, **scores},
    )
