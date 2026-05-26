from __future__ import annotations

from apps.common.exceptions import ConflictError, NotFoundError


class WishlistItemExistsError(ConflictError):
    code = "WISHLIST_ITEM_EXISTS"

    def __init__(self) -> None:
        super().__init__("This fund is already in your wishlist.")


class WishlistItemNotFoundError(NotFoundError):
    code = "WISHLIST_ITEM_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Wishlist item not found.")
