from __future__ import annotations

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def download_bytes(*, key: str) -> bytes:
    """Download raw bytes from S3 by storage key."""
    with default_storage.open(key, "rb") as f:
        return f.read()


def upload_bytes(
    *,
    key: str,
    data: bytes,
    content_type: str,
) -> None:
    """Upload raw bytes to S3, overwriting if exists."""
    if default_storage.exists(key):
        default_storage.delete(key)
    default_storage.save(key, ContentFile(data, name=key))
