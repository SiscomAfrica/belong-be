from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import SessionNotFoundError
from apps.ai_profiler.models import ConversationSession


def get_session(*, session_id: UUID, user_id: UUID) -> ConversationSession:
    try:
        return ConversationSession.objects.prefetch_related("messages").get(
            id=session_id, user_id=user_id,
        )
    except ConversationSession.DoesNotExist:
        raise SessionNotFoundError() from None
