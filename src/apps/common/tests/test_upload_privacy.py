from __future__ import annotations

import pytest
from django.test import override_settings

from apps.common.exceptions import ValidationError
from apps.common.services.media_routing import bucket_for, is_public, is_uploadable
from apps.common.services.s3 import generate_presigned_download, generate_presigned_upload

PRIVATE = "belong-bucket"
PUBLIC = "belong-media"

routed = override_settings(
    AWS_STORAGE_BUCKET_NAME=PRIVATE,
    PUBLIC_MEDIA_BUCKET=PUBLIC,
    PUBLIC_MEDIA_URL="https://media.belong.club",
)


@routed
def test_profile_photos_are_private() -> None:
    """A profile photo is a picture of someone's face — it stays behind auth."""
    key = "profile-photos/9f/me.jpg"

    assert not is_public(key)
    assert bucket_for(key) == PRIVATE
    assert "X-Amz-Signature" in generate_presigned_download(file_key=key)["download_url"]


@routed
def test_kyc_documents_are_private() -> None:
    for key in ("kyc-documents/a/front.jpg", "kyc-selfies/a/me.jpg"):
        assert not is_public(key)
        assert bucket_for(key) == PRIVATE


@routed
def test_catalogue_art_stays_public() -> None:
    for key in ("hero_images/funds/a.jpg", "holding_logos/f/l.png"):
        assert is_public(key)
        assert bucket_for(key) == PUBLIC


def test_only_known_folders_may_be_uploaded_into() -> None:
    assert is_uploadable("kyc-documents")
    assert is_uploadable("profile-photos")
    assert not is_uploadable("../../etc")
    assert not is_uploadable("anything-else")


@routed
def test_an_unknown_folder_is_rejected_not_silently_accepted() -> None:
    """The folder decides the bucket, so it cannot come unchecked from a client."""
    with pytest.raises(ValidationError):
        generate_presigned_upload(
            folder="totally-made-up", filename="x.jpg", content_type="image/jpeg",
        )


@routed
def test_a_client_cannot_upload_straight_into_public_storage() -> None:
    """hero_images is uploadable, but only staff reach the admin that writes it.

    The check that matters is that an arbitrary string cannot reach the public
    bucket — a caller has to name a folder we chose.
    """
    with pytest.raises(ValidationError):
        generate_presigned_upload(
            folder="hero_images/../profile-photos",
            filename="x.jpg",
            content_type="image/jpeg",
        )
