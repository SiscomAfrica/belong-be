from __future__ import annotations

from ninja import Router

from apps.payments.schemas import WalletTopUpIn
from apps.payments.schemas.output import PaymentInitiateOut
from apps.payments.schemas.output_wallet import WalletOut
from apps.payments.selectors.get_wallet import get_wallet
from apps.payments.services.initiate_wallet_topup import initiate_wallet_topup
from config.throttles import payment_initiation_throttles

wallet_router = Router(tags=["wallet"])


@wallet_router.get("/", response=WalletOut)
def get_my_wallet(request):
    """Return the authenticated user's wallet balance."""
    return get_wallet(user_id=request.auth.id)


@wallet_router.post(
    "/topup/",
    response={201: PaymentInitiateOut},
    throttle=payment_initiation_throttles(),
)
def topup_wallet(request, payload: WalletTopUpIn):
    """Add money to the wallet, with no investment attached.

    Shares the payment-initiation throttle with /payments/initiate/, because
    it is the same thing from the abuse side: a request that makes Safaricom
    send someone an STK prompt.
    """
    txn = initiate_wallet_topup(
        user_id=request.auth.id,
        amount=payload.amount,
        provider=payload.provider,
        phone_number=payload.phone_number or request.auth.phone,
        idempotency_key=payload.idempotency_key,
    )
    return 201, {"transaction": txn, "authorization_url": txn.authorization_url}
