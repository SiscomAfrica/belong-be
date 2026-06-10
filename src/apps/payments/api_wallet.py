from __future__ import annotations

from ninja import Router

from apps.payments.schemas.output_wallet import WalletOut
from apps.payments.selectors.get_wallet import get_wallet

wallet_router = Router(tags=["wallet"])


@wallet_router.get("/", response=WalletOut)
def get_my_wallet(request):  # noqa: ANN001, ANN201
    """Return the authenticated user's wallet balance."""
    return get_wallet(user_id=request.auth.id)
