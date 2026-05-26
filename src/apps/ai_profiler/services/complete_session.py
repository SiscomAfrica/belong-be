from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import SessionAlreadyCompletedError, SessionNotFoundError
from apps.ai_profiler.models import ConversationSession, InvestorProfile, SessionStatus
from apps.ai_profiler.services.score_investor_type import score_investor_type
from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.users.models import User
from apps.users.services.set_investor_type import set_investor_type


def complete_session(*, session_id: UUID, user_id: UUID) -> InvestorProfile:
    try:
        session = ConversationSession.objects.get(id=session_id, user_id=user_id)
    except ConversationSession.DoesNotExist:
        raise SessionNotFoundError() from None

    if session.status != SessionStatus.ACTIVE:
        raise SessionAlreadyCompletedError()

    messages = list(session.messages.all())
    scores = score_investor_type(messages=messages)

    profile, _ = InvestorProfile.objects.update_or_create(
        user_id=user_id,
        defaults={
            "risk_tolerance": scores["risk_tolerance"],
            "time_horizon": scores["time_horizon"],
            "investment_goal": scores["investment_goal"],
            "interests": scores["interests"],
        },
    )

    user = User.objects.get(pk=user_id)
    set_investor_type(user=user, investor_type=scores["investor_type"])

    session.status = SessionStatus.COMPLETED
    session.summary = f"Type: {scores['investor_type']}, Risk: {scores['risk_tolerance']}"
    session.save(update_fields=["status", "summary", "updated_at"])

    create_audit_log(
        action=AuditAction.PROFILER_COMPLETED,
        actor_id=user_id,
        entity_type="InvestorProfile",
        entity_id=profile.id,
        new_values=scores,
    )

    return profile
