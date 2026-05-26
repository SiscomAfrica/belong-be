from __future__ import annotations

from uuid import UUID

from ninja import Query, Router

from apps.payments.schemas import (
    PaymentInitiateIn,
    PaymentInitiateOut,
    PaymentListOut,
    PaymentTransactionOut,
)
from apps.payments.selectors.get_payment_transaction import get_payment_transaction
from apps.payments.selectors.list_user_payments import list_user_payments
from apps.payments.services.initiate_payment import initiate_payment

payments_router = Router(tags=["payments"])


@payments_router.post("/initiate/", response={201: PaymentInitiateOut})
def initiate(request, payload: PaymentInitiateIn):
    txn = initiate_payment(
        user_id=request.auth.id,
        investment_id=payload.investment_id,
        provider=payload.provider,
        phone_number=payload.phone_number,
        idempotency_key=payload.idempotency_key,
    )
    return 201, {"transaction": txn, "authorization_url": txn.authorization_url}


@payments_router.get("/", response=PaymentListOut)
def list_payments(
    request,
    status: str | None = Query(None),
    provider: str | None = Query(None),
):
    qs = list_user_payments(
        user_id=request.auth.id, status=status, provider=provider,
    )
    return {"items": list(qs), "count": qs.count()}


@payments_router.get("/{transaction_id}", response=PaymentTransactionOut)
def detail(request, transaction_id: UUID):
    return get_payment_transaction(
        transaction_id=transaction_id, user_id=request.auth.id,
    )
