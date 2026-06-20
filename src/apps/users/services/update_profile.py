from __future__ import annotations

from apps.users.models import User


def update_profile(
    *,
    user: User,
    first_name: str | None = None,
    last_name: str | None = None,
    preferred_currency: str | None = None,
    profile_image_key: str | None = None,
) -> User:
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if preferred_currency is not None:
        user.preferred_currency = preferred_currency
    if profile_image_key is not None:
        user.profile_image_key = profile_image_key

    user.save(update_fields=[
        "first_name", "last_name", "preferred_currency",
        "profile_image_key", "updated_at",
    ])
    return user
