from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.wishlist.models import WishlistItem


def list_user_wishlist(*, user_id: UUID) -> QuerySet[WishlistItem]:
    return (
        WishlistItem.objects.filter(user_id=user_id)
        .select_related("fund")
    )
