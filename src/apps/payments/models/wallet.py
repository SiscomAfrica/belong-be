from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class Wallet(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance_ksh = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance_usd = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        db_table = "payments_wallet"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Wallet: {self.user_id}"
