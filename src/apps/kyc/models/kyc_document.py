from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class DocumentSide(models.TextChoices):
    FRONT = "FRONT", "Front"
    BACK = "BACK", "Back"
    SELFIE = "SELFIE", "Selfie"


class KYCDocument(BaseModel):
    submission = models.ForeignKey(
        "kyc.KYCSubmission",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    side = models.CharField(max_length=10, choices=DocumentSide.choices)
    file_key = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kyc_document"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "side"], name="unique_submission_side",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.side} for submission {self.submission_id}"
