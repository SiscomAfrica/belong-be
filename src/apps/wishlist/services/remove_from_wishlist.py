from __future__ import annotations

from uuid import UUID

from apps.wishlist.exceptions import WishlistItemNotFoundError
from apps.wishlist.models import WishlistItem


def remove_from_wishlist(*, user_id: UUID, fund_id: UUID) -> None:
    deleted, _ = WishlistItem.objects.filter(
        user_id=user_id,
        fund_id=fund_id,
    ).delete()

    if deleted == 0:
        raise WishlistItemNotFoundError()
