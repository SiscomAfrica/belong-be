from __future__ import annotations

from uuid import UUID

from apps.users.models import User


def build_context(*, user_id: UUID) -> str:
    user = User.objects.get(pk=user_id)
    parts = [
        f"User: {user.first_name or 'Unknown'} {user.last_name or ''}".strip(),
        f"Phone: {user.phone}",
        f"Current investor type: {user.investor_type or 'Not set'}",
    ]

    if hasattr(user, "kyc_submissions"):
        kyc = user.kyc_submissions.order_by("-created_at").first()
        parts.append(f"KYC status: {kyc.status if kyc else 'No submission'}")

    holdings = _get_holdings_summary(user_id=user_id)
    if holdings:
        parts.append(f"Current holdings: {holdings}")

    prior = _get_prior_summaries(user_id=user_id)
    if prior:
        parts.append(f"Prior session notes: {prior}")

    return "\n".join(parts)


def _get_holdings_summary(*, user_id: UUID) -> str:
    from apps.investments.models import Holding

    holdings = Holding.objects.filter(user_id=user_id).select_related("fund")
    if not holdings.exists():
        return ""
    return ", ".join(f"{h.fund.name}: {h.total_invested}" for h in holdings[:5])


def _get_prior_summaries(*, user_id: UUID) -> str:
    from apps.ai_profiler.models import ConversationSession, SessionStatus

    sessions = ConversationSession.objects.filter(
        user_id=user_id, status=SessionStatus.COMPLETED,
    ).order_by("-created_at")[:3]
    return " | ".join(s.summary for s in sessions if s.summary)
