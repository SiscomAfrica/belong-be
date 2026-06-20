# from __future__ import annotations
#
# from uuid import UUID
#
# from django.utils import timezone
#
# from apps.kyc.exceptions import KYCInvalidStateError, KYCNotFoundError, KYCProviderError
# from apps.kyc.models import KYCDocument, KYCStatus, KYCSubmission
# from apps.kyc.models.kyc_document import DocumentSide
# from apps.kyc.providers.smile_identity import SmileIdentityProvider
#
#
# def upload_selfie(*, user_id: UUID, file_key: str) -> KYCSubmission:
#     try:
#         submission = KYCSubmission.objects.get(user_id=user_id)
#     except KYCSubmission.DoesNotExist:
#         raise KYCNotFoundError()
#
#     if submission.status != KYCStatus.PENDING:
#         raise KYCInvalidStateError("KYC must be in PENDING state to upload selfie.")
#
#     KYCDocument.objects.update_or_create(
#         submission=submission,
#         side=DocumentSide.SELFIE,
#         defaults={"file_key": file_key},
#     )
#     documents = list(submission.documents.all())
#     images = [{"image_type_id": doc.side, "image": doc.file_key} for doc in documents]
#
#     provider = SmileIdentityProvider()
#     result = provider.submit_verification(
#         partner_params={"user_id": str(user_id), "job_id": str(submission.id)},
#         images=images,
#     )
#     submission.status = KYCStatus.PROCESSING
#     submission.smile_job_id = result.job_id
#     submission.submitted_at = timezone.now()
#     submission.save()
#     return KYCSubmission.objects.prefetch_related("documents").get(pk=submission.pk)
