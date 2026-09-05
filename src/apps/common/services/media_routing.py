from __future__ import annotations

from django.conf import settings

# Which key prefixes live in the public bucket. Everything else — KYC
# documents and selfies above all — stays in the private bucket and is only
# ever reachable through a short-lived signed URL.
PUBLIC_FOLDERS = frozenset({"hero_images", "holding_logos", "profile-photos"})


def public_media_bucket() -> str:
    """Read lazily so tests can override it and a missing setting is not fatal."""
    return getattr(settings, "PUBLIC_MEDIA_BUCKET", "").strip()


def public_media_url() -> str:
    return getattr(settings, "PUBLIC_MEDIA_URL", "").rstrip("/")


def is_public(file_key: str) -> bool:
    return file_key.split("/", 1)[0] in PUBLIC_FOLDERS


def bucket_for(file_key: str) -> str:
    """The bucket an object belongs in, by key prefix.

    Falls back to the private bucket while the public one is unconfigured, so
    a half-finished setup serves signed URLs rather than 404s.
    """
    if is_public(file_key) and public_media_bucket():
        return public_media_bucket()
    return settings.AWS_STORAGE_BUCKET_NAME
