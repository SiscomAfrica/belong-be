from __future__ import annotations

from ninja import Query, Router

from apps.payments.schemas import (
    WithdrawalCreateIn,
    WithdrawalListOut,
    WithdrawalOut,
)
from apps.payments.selectors.list_withdrawal_requests import list_withdrawal_requests
from apps.payments.services.create_withdrawal_request import create_withdrawal_request

withdrawals_router = Router(tags=["withdrawals"])


@withdrawals_router.post("/", response={201: WithdrawalOut})
def create(request, payload: WithdrawalCreateIn):
    withdrawal = create_withdrawal_request(
        user_id=request.auth.id,
        amount=payload.amount,
        phone_number=payload.phone_number,
    )
    return 201, withdrawal


@withdrawals_router.get("/", response=WithdrawalListOut)
def list_withdrawals(
    request,
    status: str | None = Query(None),
):
    qs = list_withdrawal_requests(user_id=request.auth.id, status=status)
    return {"items": list(qs), "count": qs.count()}
