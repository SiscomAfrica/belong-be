from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class KYCStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not Started"
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"
    MANUAL_REVIEW = "MANUAL_REVIEW", "Manual Review"


class DocumentType(models.TextChoices):
    NATIONAL_ID = "NATIONAL_ID", "National ID"
    PASSPORT = "PASSPORT", "Passport"
    DRIVING_LICENSE = "DRIVING_LICENSE", "Driving License"


class KYCSubmission(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="kyc_submission",
    )
    status = models.CharField(
        max_length=20, choices=KYCStatus.choices,
        default=KYCStatus.NOT_STARTED, db_index=True,
    )
    document_type = models.CharField(
        max_length=20, choices=DocumentType.choices, blank=True, default="",
    )
    smile_job_id = models.CharField(max_length=100, blank=True, default="", db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    result_text = models.TextField(blank=True, default="")

    class Meta:
        db_table = "kyc_submission"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"KYC {self.status} for {self.user_id}"
