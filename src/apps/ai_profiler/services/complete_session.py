from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import SessionAlreadyCompletedError, SessionNotFoundError
from apps.ai_profiler.models import (
    ConversationSession,
    InvestorProfile,
    ProfileTemplate,
    SessionStatus,
)
from apps.ai_profiler.rubric import MEDIAN_LEVEL, ORDINAL_KEYS
from apps.ai_profiler.selectors.get_session_signals import get_session_signals
from apps.ai_profiler.services.match_profile import match_profile
from apps.ai_profiler.services.score_vector import score_vector
from apps.ai_profiler.services.summarise_profile import horizon_label, summarise
from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.users.models import User
from apps.users.services.mark_onboarded import mark_onboarded
from apps.users.services.set_investor_type import set_investor_type


def complete_session(*, session_id: UUID, user_id: UUID) -> InvestorProfile:
    """Score the session and assign an investor profile.

    The LLM never reaches this function. It sees only anchors the user selected,
    so two sessions with matching anchors resolve to the same profile however
    differently their questions were worded.
    """
    session = _active_session(session_id=session_id, user_id=user_id)

    signals = get_session_signals(session_id=session_id)
    vector = score_vector(signals=signals)
    imputed = [key for key in ORDINAL_KEYS if vector.get(key) is None]

    templates = list(ProfileTemplate.objects.filter(is_active=True))
    matched = match_profile(
        vector=vector,
        profiles=[
            {"investor_type": t.investor_type, "centroid": t.centroid or {}, "template": t}
            for t in templates
            if t.centroid
        ],
    )
    investor_type = matched["investor_type"]

    profile, _ = InvestorProfile.objects.update_or_create(
        user_id=user_id,
        defaults={
            "risk_tolerance": vector.get("risk") or MEDIAN_LEVEL,
            "time_horizon": horizon_label(level=vector.get("horizon")),
            "investment_goal": vector.get("motivation") or "",
            "interests": [vector["market"]] if vector.get("market") else [],
            "behaviour_vector": vector,
            "imputed_behaviours": imputed,
        },
    )

    user = User.objects.get(pk=user_id)
    set_investor_type(user=user, investor_type=investor_type)
    mark_onboarded(user=user)

    session.status = SessionStatus.COMPLETED
    session.summary = summarise(investor_type=investor_type, vector=vector)
    session.save(update_fields=["status", "summary", "updated_at"])

    create_audit_log(
        action=AuditAction.PROFILER_COMPLETED,
        actor_id=user_id,
        entity_type="InvestorProfile",
        entity_id=profile.id,
        new_values={
            "investor_type": investor_type,
            "vector": vector,
            "imputed": imputed,
        },
    )

    return profile


def _active_session(*, session_id: UUID, user_id: UUID) -> ConversationSession:
    try:
        session = ConversationSession.objects.get(id=session_id, user_id=user_id)
    except ConversationSession.DoesNotExist:
        raise SessionNotFoundError() from None

    if session.status != SessionStatus.ACTIVE:
        raise SessionAlreadyCompletedError()

    return session
