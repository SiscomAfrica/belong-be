from __future__ import annotations

import uuid

from apps.common.exceptions import PermissionDeniedError, ValidationError
from apps.common.services.media_routing import (
    UPLOAD_FOLDERS,
    bucket_for,
    is_public,
    is_uploadable,
    public_media_url,
)
from apps.common.services.s3_client import (
    DOWNLOAD_EXPIRY,
    UPLOAD_EXPIRY,
    get_s3_client,
)

# Re-exported: callers and tests import these from here, and the split into
# s3_client was to hold this file under the line limit, not to move the
# public surface.
__all__ = [
    "DOWNLOAD_EXPIRY",
    "UPLOAD_EXPIRY",
    "generate_presigned_download",
    "generate_presigned_upload",
    "get_s3_client",
]


def generate_presigned_upload(
    *,
    folder: str,
    filename: str,
    content_type: str,
    is_staff: bool = False,
) -> dict:
    if not is_uploadable(folder):
        # The folder decides the bucket, so an unchecked value from the client
        # is a way to write into public storage.
        allowed = ", ".join(sorted(UPLOAD_FOLDERS))
        raise ValidationError(f"Unknown upload folder. Expected one of: {allowed}.")

    if is_public(folder) and not is_staff:
        # These folders serve unauthenticated from media.belong.club under
        # permanent URLs, and `filename` reaches the key — so without this any
        # registered user could presign hero_images/<uuid>/evil.html and host
        # it on the media domain. Content-Type cannot be the control here: it
        # is no longer signed (below), so R2 stores whatever the client sends.
        raise PermissionDeniedError(
            "Catalogue images are uploaded through the admin.",
        )

    file_key = f"{folder}/{uuid.uuid4()}/{filename}"
    # `content_type` is accepted but deliberately NOT signed. Signing it puts
    # content-type into SignedHeaders and R2 then 403s the PUT unless the
    # client's header matches byte for byte — which React Native cannot
    # promise, because BlobModule.toRequestBody overrides the header with the
    # blob's own `type` (application/octet-stream when it has none). Nothing
    # is given up: content_type came from the client either way.
    upload_url = get_s3_client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket_for(file_key),
            "Key": file_key,
        },
        ExpiresIn=UPLOAD_EXPIRY,
    )
    return {
        "upload_url": upload_url,
        "file_key": file_key,
        "expires_in": UPLOAD_EXPIRY,
    }


def generate_presigned_download(*, file_key: str) -> dict:
    """A URL for a stored object.

    Public folders get a permanent CDN URL rather than a signature. Signing
    them was what stopped every cache from ever hitting: the query string
    changed on every response, so Cloudflare, the OS and the app's own image
    cache each saw a brand-new image and re-downloaded the whole catalogue.
    """
    if is_public(file_key) and public_media_url():
        return {
            "download_url": f"{public_media_url()}/{file_key}",
            "expires_in": DOWNLOAD_EXPIRY,
        }

    download_url = get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_for(file_key), "Key": file_key},
        ExpiresIn=DOWNLOAD_EXPIRY,
    )
    return {
        "download_url": download_url,
        "expires_in": DOWNLOAD_EXPIRY,
    }
