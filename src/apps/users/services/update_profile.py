from __future__ import annotations

from apps.common.tasks import convert_image_to_webp
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

    if profile_image_key is not None:
        convert_image_to_webp.delay(
            profile_image_key,
            user._meta.label,
            str(user.pk),
        )

    return user
