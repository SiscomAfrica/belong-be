from __future__ import annotations

from apps.compliance.models import ConsentVersion


def get_latest_consent(*, document_type: str) -> ConsentVersion | None:
    return (
        ConsentVersion.objects.filter(document_type=document_type)
        .order_by("-effective_date")
        .first()
    )
