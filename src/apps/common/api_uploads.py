from __future__ import annotations

from ninja import Router

from apps.common.schemas.upload import (
    DownloadUrlIn,
    DownloadUrlOut,
    PresignedUploadIn,
    PresignedUploadOut,
)
from apps.common.services.s3 import (
    generate_presigned_download,
    generate_presigned_upload,
)

uploads_router = Router()


@uploads_router.post("/presigned", response=PresignedUploadOut)
def presigned_upload(request, payload: PresignedUploadIn):  # noqa: ANN001, ANN201
    return generate_presigned_upload(
        folder=payload.folder,
        filename=payload.filename,
        content_type=payload.content_type,
    )


@uploads_router.post("/download-url", response=DownloadUrlOut)
def download_url(request, payload: DownloadUrlIn):  # noqa: ANN001, ANN201
    return generate_presigned_download(file_key=payload.file_key)
