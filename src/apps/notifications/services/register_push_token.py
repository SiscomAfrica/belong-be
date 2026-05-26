from __future__ import annotations

from uuid import UUID

from apps.notifications.models import DevicePushToken


def register_push_token(
    *,
    user_id: UUID,
    token: str,
    platform: str,
) -> DevicePushToken:
    push_token, _created = DevicePushToken.objects.update_or_create(
        token=token,
        defaults={
            "user_id": user_id,
            "platform": platform,
            "is_active": True,
        },
    )
    return push_token
