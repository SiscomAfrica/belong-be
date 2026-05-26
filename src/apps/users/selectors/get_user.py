from __future__ import annotations

from uuid import UUID

from apps.common.exceptions import NotFoundError
from apps.users.models import User


def get_user(*, user_id: UUID) -> User:
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise NotFoundError("User not found")
