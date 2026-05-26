from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class PaymentProvider(models.TextChoices):
    MPESA = "MPESA", "M-Pesa"
    PAYSTACK = "PAYSTACK", "Paystack"


class PaymentStatus(models.TextChoices):
    INITIATED = "INITIATED", "Initiated"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"
    EXPIRED = "EXPIRED", "Expired"


class PaymentTransaction(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="payment_transactions",
    )
    investment = models.ForeignKey(
        "investments.Investment", on_delete=models.PROTECT,
        related_name="payment_transactions", null=True, blank=True,
    )
    provider = models.CharField(max_length=10, choices=PaymentProvider.choices, db_index=True)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices,
        default=PaymentStatus.INITIATED, db_index=True,
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    phone_number = models.CharField(max_length=20, blank=True, default="")
    external_ref = models.CharField(max_length=100, unique=True, db_index=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, default="")
    authorization_url = models.URLField(blank=True, default="")
    provider_response = models.JSONField(default=dict)
    failure_reason = models.CharField(max_length=255, blank=True, default="")
    idempotency_key = models.CharField(max_length=64, unique=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments_transaction"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.provider} - {self.external_ref} - {self.status}"
