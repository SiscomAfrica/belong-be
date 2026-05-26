from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.ai_profiler.models import ConversationSession


def list_user_sessions(*, user_id: UUID) -> QuerySet[ConversationSession]:
    return ConversationSession.objects.filter(user_id=user_id).order_by("-created_at")
