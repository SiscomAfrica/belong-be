from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class NotificationType(models.TextChoices):
    INVESTMENT_CONFIRMED = "INVESTMENT_CONFIRMED", "Investment Confirmed"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED", "Payment Received"
    PAYMENT_FAILED = "PAYMENT_FAILED", "Payment Failed"
    KYC_APPROVED = "KYC_APPROVED", "KYC Approved"
    KYC_REJECTED = "KYC_REJECTED", "KYC Rejected"
    WITHDRAWAL_PROCESSED = "WITHDRAWAL_PROCESSED", "Withdrawal Processed"
    RECURRING_PLAN_EXECUTED = "RECURRING_PLAN_EXECUTED", "Recurring Plan Executed"
    YIELD_ALERT = "YIELD_ALERT", "Yield Alert"
    REFERRAL_CONVERTED = "REFERRAL_CONVERTED", "Referral Converted"
    STATEMENT_READY = "STATEMENT_READY", "Statement Ready"
    PROFILER_COMPLETED = "PROFILER_COMPLETED", "Profiler Completed"
    GENERAL = "GENERAL", "General"


class Notification(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=40, choices=NotificationType.choices, db_index=True)
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=1000)
    is_read = models.BooleanField(default=False, db_index=True)
    action_url = models.CharField(max_length=500, blank=True, default="")
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "notifications_notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self) -> str:
        return f"{self.type} -> {self.user_id}"
