from __future__ import annotations

from uuid import UUID

from ninja import Router

from apps.wishlist.schemas import WishlistAddIn, WishlistItemOut, WishlistListOut
from apps.wishlist.selectors import list_user_wishlist
from apps.wishlist.services import add_to_wishlist, remove_from_wishlist

wishlist_router = Router(tags=["wishlist"])


@wishlist_router.post("/", response={201: WishlistItemOut})
def add(request, payload: WishlistAddIn):  # noqa: ANN001, ANN201
    """Add a fund to the user's wishlist."""
    item = add_to_wishlist(user_id=request.auth.id, fund_id=payload.fund_id)
    return 201, item


@wishlist_router.delete("/{fund_id}", response={204: None})
def remove(request, fund_id: UUID):  # noqa: ANN001, ANN201
    """Remove a fund from the user's wishlist."""
    remove_from_wishlist(user_id=request.auth.id, fund_id=fund_id)
    return 204, None


@wishlist_router.get("/", response=WishlistListOut)
def list_wishlist(request):  # noqa: ANN001, ANN201
    """List all funds in the user's wishlist."""
    qs = list_user_wishlist(user_id=request.auth.id)
    return {"items": list(qs), "count": qs.count()}
