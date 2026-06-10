from __future__ import annotations

from django.http import HttpResponse
from ninja import Router

from apps.compliance.exceptions import StatementNotFoundError
from apps.compliance.models import DocumentType
from apps.compliance.schemas import (
    ConsentStatusOut,
    ConsentVersionOut,
    InvestmentLimitOut,
    RecordConsentIn,
    UserConsentOut,
)
from apps.compliance.selectors.get_latest_consent import get_latest_consent
from apps.compliance.services.check_consent_current import check_consent_current
from apps.compliance.services.generate_statement import generate_statement
from apps.compliance.services.get_user_tier import get_user_tier
from apps.compliance.services.record_consent import record_consent

compliance_router = Router(tags=["compliance"])


@compliance_router.get("/limits", response=InvestmentLimitOut)
def get_limits(request):
    """Return investment limits based on the user's KYC tier."""
    from apps.compliance.selectors.get_investment_limits import get_investment_limits

    tier = get_user_tier(user_id=request.auth.id)
    limit = get_investment_limits(kyc_tier=tier)
    if limit is None:
        return InvestmentLimitOut(kyc_tier=tier, max_per_transaction=0, max_per_month=0)
    return limit


@compliance_router.get("/consent/latest", response=list[ConsentVersionOut])
def get_latest_consents(request):
    """Return the latest consent document versions for terms and privacy."""
    results = []
    for doc_type in DocumentType:
        version = get_latest_consent(document_type=doc_type.value)
        if version:
            results.append(version)
    return results


@compliance_router.get("/consent/status", response=ConsentStatusOut)
def get_consent_status(request):
    """Check whether the user has accepted the latest consent documents."""
    status = check_consent_current(user_id=request.auth.id)
    return ConsentStatusOut(**status)


@compliance_router.post("/consent", response={201: UserConsentOut})
def accept_consent(request, payload: RecordConsentIn):
    """Record user acceptance of a consent document version."""
    ip = request.META.get("REMOTE_ADDR")
    consent = record_consent(
        user_id=request.auth.id,
        consent_version_id=payload.consent_version_id,
        ip_address=ip,
    )
    return 201, consent


@compliance_router.get("/statements/{year}/{month}")
def get_statement(request, year: int, month: int):
    """Download the user's monthly investment statement as PDF."""
    try:
        pdf_bytes = generate_statement(user_id=request.auth.id, year=year, month=month)
    except Exception:
        raise StatementNotFoundError() from None
    return HttpResponse(pdf_bytes, content_type="application/pdf")
