from __future__ import annotations

from uuid import UUID

from apps.investments.models import Investment, InvestmentStatus
from apps.kyc.selectors.get_kyc_status import get_kyc_status
from apps.payments.models.wallet import Wallet


def get_wallet(*, user_id: UUID) -> dict:
    wallet, _ = Wallet.objects.get_or_create(user_id=user_id)
    kyc = get_kyc_status(user_id=user_id)
    has_pending = Investment.objects.filter(
        user_id=user_id, status=InvestmentStatus.PENDING_KYC,
    ).exists()

    return {
        "id": wallet.id,
        "balance_ksh": wallet.balance_ksh,
        "balance_usd": wallet.balance_usd,
        "updated_at": wallet.updated_at,
        "kyc_status": kyc["status"],
        "has_pending_kyc_investments": has_pending,
    }
