from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from apps.payments.services.get_or_create_wallet import get_or_create_wallet


def balance(user_id: UUID) -> Decimal:
    """Current KSh wallet balance, creating the wallet if it does not exist."""
    return get_or_create_wallet(user_id=user_id).balance_ksh
