from __future__ import annotations

from uuid import UUID

from apps.users.models import User, UserDevice


def register_device(
    *,
    user: User,
    device_id: str,
    platform: str,
    fcm_token: str = "",
) -> UserDevice:
    device, _ = UserDevice.objects.update_or_create(
        user=user,
        device_id=device_id,
        defaults={"platform": platform, "fcm_token": fcm_token, "is_active": True},
    )
    return device


def deactivate_device(*, user: User, device_pk: UUID) -> None:
    UserDevice.objects.filter(user=user, pk=device_pk).update(is_active=False)
