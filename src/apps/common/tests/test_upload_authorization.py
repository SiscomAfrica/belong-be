from __future__ import annotations

import pytest
from django.test import override_settings

from apps.common.exceptions import PermissionDeniedError
from apps.common.services.s3 import generate_presigned_upload

routed = override_settings(
    AWS_STORAGE_BUCKET_NAME="belong-bucket",
    PUBLIC_MEDIA_BUCKET="belong-media",
    PUBLIC_MEDIA_URL="https://media.belong.club",
)


@routed
def test_an_ordinary_user_cannot_presign_into_public_storage() -> None:
    """hero_images serves unauthenticated from media.belong.club under a
    permanent URL, and `filename` reaches the key — so an ordinary account
    being able to presign one means anyone can host arbitrary content on the
    media domain. Content-Type is no defence: it is not signed, so R2 stores
    whatever the client sends at PUT time.
    """
    with pytest.raises(PermissionDeniedError):
        generate_presigned_upload(
            folder="hero_images", filename="evil.html", content_type="text/html",
        )


@routed
def test_staff_may_still_write_catalogue_art() -> None:
    result = generate_presigned_upload(
        folder="hero_images",
        filename="fund.jpg",
        content_type="image/jpeg",
        is_staff=True,
    )

    assert result["file_key"].startswith("hero_images/")


@routed
def test_an_ordinary_user_may_still_upload_their_own_documents() -> None:
    for folder in ("kyc-documents", "kyc-selfies", "profile-photos"):
        result = generate_presigned_upload(
            folder=folder, filename="x.jpg", content_type="image/jpeg",
        )
        assert result["file_key"].startswith(f"{folder}/")
