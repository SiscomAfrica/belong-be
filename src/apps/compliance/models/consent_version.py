from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class DocumentType(models.TextChoices):
    TERMS = "TERMS", "Terms of Service"
    PRIVACY = "PRIVACY", "Privacy Policy"


class ConsentVersion(BaseModel):
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    version = models.CharField(max_length=20)
    effective_date = models.DateField()
    content_url = models.URLField()

    class Meta:
        db_table = "compliance_consent_version"
        constraints = [
            models.UniqueConstraint(
                fields=["document_type", "version"],
                name="unique_consent_doc_version",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.document_type} v{self.version}"
