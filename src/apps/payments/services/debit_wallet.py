from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.db.models import F

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.payments.exceptions import InsufficientBalanceError
from apps.payments.models.wallet import Wallet
from apps.payments.services.get_or_create_wallet import get_or_create_wallet


def debit_wallet(
    *, user_id: UUID, amount: Decimal, currency: str
) -> Wallet:
    get_or_create_wallet(user_id=user_id)
    field = "balance_ksh" if currency == "KES" else "balance_usd"

    with transaction.atomic():
        wallet = Wallet.objects.select_for_update().get(user_id=user_id)
        balance = getattr(wallet, field)
        if balance < amount:
            raise InsufficientBalanceError()

        Wallet.objects.filter(user_id=user_id).update(**{field: F(field) - amount})
        wallet.refresh_from_db()

    create_audit_log(
        action=AuditAction.WALLET_DEBITED,
        actor_id=user_id,
        entity_type="Wallet",
        entity_id=wallet.id,
        new_values={"amount": str(amount), "currency": currency},
    )
    return wallet
