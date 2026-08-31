from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.models import ConversationSession, InvestorProfile, ProfileTemplate
from apps.ai_profiler.models.investor_profile import ScoringMethod
from apps.ai_profiler.rubric import MEDIAN_LEVEL, ORDINAL_KEYS
from apps.ai_profiler.selectors.get_session_signals import get_session_signals
from apps.ai_profiler.services.finalise_profile import finalise_profile
from apps.ai_profiler.services.match_profile import match_profile
from apps.ai_profiler.services.score_vector import score_vector
from apps.ai_profiler.services.summarise_profile import horizon_label, summarise


class NoScorableProfilesError(RuntimeError):
    """No active template carries a centroid, so nothing can be matched."""


def complete_rubric_session(
    *, session: ConversationSession, user_id: UUID,
) -> InvestorProfile:
    """Score a session from the anchors the user selected.

    The LLM never reaches this function. It sees only anchors, so two sessions
    with matching anchors resolve to the same profile however differently their
    questions were worded.
    """
    vector = score_vector(signals=get_session_signals(session_id=session.id))
    imputed = [key for key in ORDINAL_KEYS if vector.get(key) is None]

    candidates = [
        {"investor_type": t.investor_type, "centroid": t.centroid}
        for t in ProfileTemplate.objects.filter(is_active=True)
        if t.centroid
    ]
    if not candidates:
        msg = "No active ProfileTemplate has a centroid — run seed_profiles"
        raise NoScorableProfilesError(msg)

    investor_type = match_profile(vector=vector, profiles=candidates)["investor_type"]

    profile, _ = InvestorProfile.objects.update_or_create(
        user_id=user_id,
        defaults={
            "risk_tolerance": vector.get("risk") or MEDIAN_LEVEL,
            "time_horizon": horizon_label(level=vector.get("horizon")),
            "investment_goal": vector.get("motivation") or "",
            "interests": [vector["market"]] if vector.get("market") else [],
            "behaviour_vector": vector,
            "imputed_behaviours": imputed,
            "scoring_method": ScoringMethod.RUBRIC,
        },
    )

    return finalise_profile(
        session=session,
        user_id=user_id,
        profile=profile,
        investor_type=investor_type,
        summary=summarise(investor_type=investor_type, vector=vector),
        audit_values={
            "scoring_method": ScoringMethod.RUBRIC,
            "investor_type": investor_type,
            "vector": vector,
            "imputed": imputed,
        },
    )
