from __future__ import annotations

from django.core.files.base import ContentFile
from django.core.files.storage import Storage, default_storage

from apps.common.services.media_routing import is_public


def catalogue_storage() -> Storage:
    """Storage holding public catalogue art.

    Imported lazily: the class reads settings at construction, and this module
    is imported by Celery tasks that may load before app settings are ready.
    """
    from apps.common.storage import PublicMediaStorage

    return PublicMediaStorage()


def storage_for(file_key: str) -> Storage:
    """The storage an object actually lives in, by key prefix.

    The two buckets are addressed by different clients, so reading a private
    object through the public storage looks exactly like a missing file.
    """
    return catalogue_storage() if is_public(file_key) else default_storage


def download_bytes(*, key: str, storage: Storage | None = None) -> bytes:
    """Download raw bytes by storage key."""
    with (storage or storage_for(key)).open(key, "rb") as f:
        return f.read()


def upload_bytes(
    *,
    key: str,
    data: bytes,
    content_type: str,
    storage: Storage | None = None,
) -> None:
    """Upload raw bytes, overwriting if the key already exists."""
    target = storage or storage_for(key)
    if target.exists(key):
        target.delete(key)
    target.save(key, ContentFile(data, name=key))
