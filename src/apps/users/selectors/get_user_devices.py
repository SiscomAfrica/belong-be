from __future__ import annotations

from django.db.models import QuerySet

from apps.users.models import User, UserDevice


def get_user_devices(*, user: User, active_only: bool = True) -> QuerySet[UserDevice]:
    qs = UserDevice.objects.filter(user=user)
    if active_only:
        qs = qs.filter(is_active=True)
    return qs.select_related("user")
