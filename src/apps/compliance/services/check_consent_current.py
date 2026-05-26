from __future__ import annotations

from uuid import UUID

from apps.compliance.models import ConsentVersion, DocumentType, UserConsent


def check_consent_current(*, user_id: UUID) -> dict:
    terms = _is_current(user_id=user_id, doc_type=DocumentType.TERMS)
    privacy = _is_current(user_id=user_id, doc_type=DocumentType.PRIVACY)
    return {"terms_current": terms, "privacy_current": privacy}


def _is_current(*, user_id: UUID, doc_type: str) -> bool:
    latest = (
        ConsentVersion.objects.filter(document_type=doc_type)
        .order_by("-effective_date")
        .first()
    )
    if latest is None:
        return True

    return UserConsent.objects.filter(
        user_id=user_id, consent_version=latest,
    ).exists()
