from __future__ import annotations

from uuid import UUID

from django.db import IntegrityError

from apps.wishlist.exceptions import WishlistItemExistsError
from apps.wishlist.models import WishlistItem


def add_to_wishlist(*, user_id: UUID, fund_id: UUID) -> WishlistItem:
    try:
        item = WishlistItem.objects.create(user_id=user_id, fund_id=fund_id)
    except IntegrityError:
        raise WishlistItemExistsError()

    return (
        WishlistItem.objects.select_related("fund")
        .get(pk=item.pk)
    )
