from __future__ import annotations

from django.test import override_settings

from apps.common.services.media_routing import bucket_for, is_public
from apps.common.services.media_urls import (
    catalogue_image_field_url,
    catalogue_image_url,
)

PUBLIC_URL = "https://media.belong.club"
PUBLIC_BUCKET = "belong-media"
PRIVATE_BUCKET = "belong-bucket"
HERO = "hero_images/funds/abc.webp"
KYC = "kyc_document/9f/front.jpg"

public_media = override_settings(
    PUBLIC_MEDIA_URL=PUBLIC_URL,
    PUBLIC_MEDIA_BUCKET=PUBLIC_BUCKET,
    AWS_STORAGE_BUCKET_NAME=PRIVATE_BUCKET,
)


@public_media
def test_catalogue_art_gets_a_permanent_unsigned_url() -> None:
    """A signature here is what stopped every cache from ever hitting."""
    url = catalogue_image_url(file_key=HERO)

    assert url == f"{PUBLIC_URL}/{HERO}"
    assert "X-Amz-Signature" not in url


@public_media
def test_repeated_calls_return_the_identical_url() -> None:
    """Byte-identical, or the phone re-downloads the catalogue every visit."""
    assert catalogue_image_url(file_key=HERO) == catalogue_image_url(file_key=HERO)


def test_kyc_documents_are_not_public() -> None:
    """The whole point of the split: identity documents stay behind a signature."""
    assert is_public(HERO)
    assert not is_public(KYC)


@public_media
def test_each_key_is_routed_to_the_bucket_it_lives_in() -> None:
    assert bucket_for(HERO) == PUBLIC_BUCKET
    assert bucket_for(KYC) == PRIVATE_BUCKET


@override_settings(PUBLIC_MEDIA_URL="", PUBLIC_MEDIA_BUCKET="")
def test_unconfigured_public_bucket_falls_back_to_private() -> None:
    """A half-finished setup must serve signed URLs, not 404s."""
    assert bucket_for(HERO) == bucket_for(KYC)


@public_media
def test_absolute_urls_from_seed_data_pass_through_untouched() -> None:
    external = "https://cdn.example.com/logo.png"

    assert catalogue_image_url(file_key=external) == external


def test_missing_image_resolves_to_empty_not_a_broken_url() -> None:
    assert catalogue_image_url(file_key="") == ""
    assert catalogue_image_field_url(image=None, fallback_key="") == ""


@public_media
def test_uploaded_file_wins_over_the_legacy_url_column() -> None:
    class Uploaded:
        name = HERO

    resolved = catalogue_image_field_url(
        image=Uploaded(), fallback_key="https://old.example.com/x.png",
    )

    assert resolved == f"{PUBLIC_URL}/{HERO}"
