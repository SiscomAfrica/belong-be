from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.models import ConversationMessage, ConversationSession, MessageRole
from apps.ai_profiler.services.build_context import build_context


def start_session(*, user_id: UUID) -> ConversationSession:
    session = ConversationSession.objects.create(user_id=user_id)

    system_prompt = build_context(user_id=user_id)
    ConversationMessage.objects.create(
        session=session,
        role=MessageRole.SYSTEM,
        content=system_prompt,
    )

    return session
