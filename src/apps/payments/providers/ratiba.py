from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

import httpx
from django.conf import settings

from apps.payments.exceptions import PaymentProviderError
from apps.payments.providers.mpesa_auth import get_mpesa_access_token, mpesa_base_url
from apps.payments.providers.ratiba_request import build_create_payload

_CREATE_PATH = "/standingorder/v1/createStandingOrderExternal"


@dataclass
class RatibaCreateResult:
    response_ref_id: str
    response_code: str
    description: str
    raw_response: dict = field(default_factory=dict)


class RatibaProvider:
    """M-Pesa Ratiba — customer-authorised standing orders.

    Creating one does not move money. Safaricom sends the customer an NI Push
    prompt; the order only becomes live once they enter their M-PESA PIN, and
    every later deduction arrives as a callback.
    """

    def create_standing_order(
        self,
        *,
        name: str,
        amount: Decimal,
        phone_number: str,
        frequency: str,
        start: date,
        end: date,
        account_reference: str,
        description: str,
        custom_sto_id: UUID,
    ) -> RatibaCreateResult:
        if not getattr(settings, "MPESA_RATIBA_ENABLED", False):
            raise PaymentProviderError("M-Pesa Ratiba is not enabled.")

        payload = build_create_payload(
            name=name,
            amount=amount,
            phone_number=phone_number,
            frequency=frequency,
            start=start,
            end=end,
            account_reference=account_reference,
            description=description,
            custom_sto_id=custom_sto_id,
        )

        try:
            resp = httpx.post(
                f"{mpesa_base_url()}{_CREATE_PATH}",
                json=payload,
                headers={"Authorization": f"Bearer {get_mpesa_access_token()}"},
                timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise PaymentProviderError(f"Ratiba create failed: {e}") from e

        return _parse_create_response(data=resp.json())


def _parse_create_response(*, data: dict) -> RatibaCreateResult:
    header = data.get("ResponseHeader") or data.get("responseHeader") or {}
    code = str(header.get("responseCode", ""))
    description = str(header.get("responseDescription", ""))

    # "200" is Ratiba's accepted-for-processing code in the body, not the HTTP
    # status — a 200 OK can still carry a rejection here.
    if code != "200":
        raise PaymentProviderError(f"Ratiba rejected the standing order: {description}")

    return RatibaCreateResult(
        response_ref_id=str(header.get("responseRefID", "")),
        response_code=code,
        description=description,
        raw_response=data,
    )
