from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.models import ConversationSession, InvestorProfile, SessionStatus
from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.users.models import User
from apps.users.services.mark_onboarded import mark_onboarded
from apps.users.services.set_investor_type import set_investor_type


def finalise_profile(
    *,
    session: ConversationSession,
    user_id: UUID,
    profile: InvestorProfile,
    investor_type: str,
    summary: str,
    audit_values: dict,
) -> InvestorProfile:
    """Close out a scored session, whichever path produced the score.

    Shared by the rubric path and the legacy path so the two cannot drift on
    what it means for onboarding to be finished.
    """
    user = User.objects.get(pk=user_id)
    set_investor_type(user=user, investor_type=investor_type)
    mark_onboarded(user=user)

    session.status = SessionStatus.COMPLETED
    session.summary = summary
    session.save(update_fields=["status", "summary", "updated_at"])

    create_audit_log(
        action=AuditAction.PROFILER_COMPLETED,
        actor_id=user_id,
        entity_type="InvestorProfile",
        entity_id=profile.id,
        new_values=audit_values,
    )

    return profile
