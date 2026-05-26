from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class WithdrawalStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    PROCESSED = "PROCESSED", "Processed"
    REJECTED = "REJECTED", "Rejected"


class WithdrawalRequest(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="withdrawal_requests",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=WithdrawalStatus.choices,
        default=WithdrawalStatus.PENDING, db_index=True,
    )
    phone_number = models.CharField(max_length=20)
    admin_notes = models.TextField(blank=True, default="")
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="processed_withdrawals",
    )

    class Meta:
        db_table = "payments_withdrawal_request"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} - {self.amount} - {self.status}"
