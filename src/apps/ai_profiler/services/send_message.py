from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import SessionAlreadyCompletedError, SessionNotFoundError
from apps.ai_profiler.models import (
    ConversationMessage,
    ConversationSession,
    MessageRole,
    SessionStatus,
)
from apps.ai_profiler.providers import get_llm_provider

SYSTEM_PROMPT = (
    "You are an investment profiler for Belong, a Kenyan investment platform. "
    "Ask questions to determine the user's risk tolerance, investment goals, "
    "time horizon, and interests. Be conversational and friendly."
)


def send_message(*, session_id: UUID, user_id: UUID, content: str) -> ConversationMessage:
    try:
        session = ConversationSession.objects.get(id=session_id, user_id=user_id)
    except ConversationSession.DoesNotExist:
        raise SessionNotFoundError() from None

    if session.status != SessionStatus.ACTIVE:
        raise SessionAlreadyCompletedError()

    ConversationMessage.objects.create(
        session=session, role=MessageRole.USER, content=content,
    )

    messages = _build_message_history(session=session)
    system = session.messages.filter(role=MessageRole.SYSTEM).first()
    system_text = f"{SYSTEM_PROMPT}\n\nContext:\n{system.content}" if system else SYSTEM_PROMPT

    provider = get_llm_provider()
    reply = provider.complete(messages=messages, system_prompt=system_text)

    return ConversationMessage.objects.create(
        session=session, role=MessageRole.ASSISTANT, content=reply,
    )


def _build_message_history(*, session: ConversationSession) -> list[dict]:
    msgs = session.messages.exclude(role=MessageRole.SYSTEM).order_by("created_at")
    return [{"role": m.role.lower(), "content": m.content} for m in msgs]
