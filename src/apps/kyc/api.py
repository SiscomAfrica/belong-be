from __future__ import annotations

from ninja import Router

from apps.kyc.schemas import (
    KYCDocumentUploadIn,
    KYCSelfieUploadIn,
    KYCStartIn,
    KYCStatusOut,
    KYCSubmissionOut,
    KYCWebhookAckOut,
)
from apps.kyc.selectors import get_kyc_status
from apps.kyc.services import process_kyc_webhook, start_kyc, upload_document, upload_selfie

kyc_router = Router(tags=["kyc"])


@kyc_router.post("/start", response={201: KYCSubmissionOut})
def start(request, payload: KYCStartIn):  # noqa: ANN001, ANN201
    """Start a new KYC verification submission."""
    submission = start_kyc(user_id=request.auth.id, document_type=payload.document_type)
    return 201, submission


@kyc_router.post("/documents", response={201: KYCSubmissionOut})
def upload_doc(request, payload: KYCDocumentUploadIn):  # noqa: ANN001, ANN201
    """Upload an ID document image (front or back) for KYC."""
    submission = upload_document(
        user_id=request.auth.id, side=payload.side, file_key=payload.file_key,
    )
    return 201, submission


@kyc_router.post("/selfie", response={201: KYCSubmissionOut})
def upload_self(request, payload: KYCSelfieUploadIn):  # noqa: ANN001, ANN201
    """Upload a selfie image for liveness verification."""
    submission = upload_selfie(user_id=request.auth.id, file_key=payload.file_key)
    return 201, submission


@kyc_router.post("/webhook", response=KYCWebhookAckOut, auth=None)
def webhook(request, payload: dict):  # noqa: ANN001, ANN201
    """Receive KYC verification results from Smile Identity."""
    process_kyc_webhook(payload=payload)
    return {"status": "received"}


@kyc_router.get("/status", response=KYCStatusOut)
def status(request):  # noqa: ANN001, ANN201
    """Return the authenticated user's current KYC verification status."""
    return get_kyc_status(user_id=request.auth.id)
