from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class CredsLedger(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="creds_entries",
    )
    delta = models.IntegerField()
    reason = models.CharField(max_length=100)
    balance_after = models.IntegerField()

    class Meta:
        db_table = "referrals_creds_ledger"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs) -> None:  # type: ignore[override]
        if self.pk and CredsLedger.objects.filter(pk=self.pk).exists():
            raise ValueError("CredsLedger records are immutable.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:  # type: ignore[override]
        raise ValueError("CredsLedger records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.user_id}: {self.delta:+d} ({self.reason})"
