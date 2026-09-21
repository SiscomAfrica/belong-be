from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from django.test import override_settings

from apps.common.services.s3 import generate_presigned_upload

routed = override_settings(
    AWS_STORAGE_BUCKET_NAME="belong-bucket",
    PUBLIC_MEDIA_BUCKET="belong-media",
    PUBLIC_MEDIA_URL="https://media.belong.club",
)


def signed_headers(upload_url: str) -> set[str]:
    query = parse_qs(urlparse(upload_url).query)
    raw = query.get("X-Amz-SignedHeaders", [""])[0]
    return {part for part in raw.split(";") if part}


@routed
def test_content_type_is_not_signed() -> None:
    """Signing content-type makes every upload hostage to the client's header.

    R2 answers 403 unless the PUT's Content-Type matches the signed value
    exactly, and React Native cannot guarantee it: BlobModule.toRequestBody
    replaces the header with the blob's own `type`, or sends
    application/octet-stream when the blob has none. That 403'd every KYC
    document and selfie upload from the Expo app.
    """
    result = generate_presigned_upload(
        folder="kyc-documents",
        filename="front.jpg",
        content_type="image/jpeg",
    )

    assert "content-type" not in signed_headers(result["upload_url"])


@routed
def test_host_is_still_signed() -> None:
    """Dropping content-type must not quietly drop the whole SignedHeaders set."""
    result = generate_presigned_upload(
        folder="kyc-selfies",
        filename="me.jpg",
        content_type="image/jpeg",
    )

    assert "host" in signed_headers(result["upload_url"])
