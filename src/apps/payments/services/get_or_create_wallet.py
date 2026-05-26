from __future__ import annotations

from uuid import UUID

from apps.payments.models.wallet import Wallet


def get_or_create_wallet(*, user_id: UUID) -> Wallet:
    wallet, _ = Wallet.objects.get_or_create(user_id=user_id)
    return wallet
