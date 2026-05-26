from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class KYCWebhookLog(BaseModel):
    submission = models.ForeignKey(
        "kyc.KYCSubmission",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhook_logs",
    )
    raw_payload = models.JSONField()
    processed_at = models.DateTimeField(null=True, blank=True)
    result_code = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        db_table = "kyc_webhook_log"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Webhook log {self.id}"
