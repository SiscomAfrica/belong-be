from __future__ import annotations

from django.conf import settings

# Catalogue art: the same file for every user, and safe to serve from a
# permanent public URL.
PUBLIC_FOLDERS = frozenset({"hero_images", "holding_logos"})

# Everything a client may upload into. Private by default — a folder has to be
# named in PUBLIC_FOLDERS as well to become world-readable.
#
# `profile-photos` is deliberately NOT public. A profile photo is a picture of
# someone's face: unguessable in practice, but a permanent unauthenticated URL
# is still an image of a real person that outlives their account. It costs one
# signature per load to keep it behind access control, which is worth it.
UPLOAD_FOLDERS = frozenset(
    {"kyc-documents", "kyc-selfies", "profile-photos"} | PUBLIC_FOLDERS,
)


def public_media_bucket() -> str:
    """Read lazily so tests can override it and a missing setting is not fatal."""
    return getattr(settings, "PUBLIC_MEDIA_BUCKET", "").strip()


def public_media_url() -> str:
    return getattr(settings, "PUBLIC_MEDIA_URL", "").rstrip("/")


def folder_of(file_key: str) -> str:
    return file_key.split("/", 1)[0]


def is_public(file_key: str) -> bool:
    return folder_of(file_key) in PUBLIC_FOLDERS


def is_uploadable(folder: str) -> bool:
    """Whether a client may request a presigned upload into this folder.

    The folder arrives from the client and decides which bucket the object
    lands in, so an unchecked value lets a caller drop a file straight into
    public storage. Only names we chose are accepted.
    """
    return folder in UPLOAD_FOLDERS


def bucket_for(file_key: str) -> str:
    """The bucket an object belongs in, by key prefix.

    Falls back to the private bucket while the public one is unconfigured, so
    a half-finished setup serves signed URLs rather than 404s.
    """
    if is_public(file_key) and public_media_bucket():
        return public_media_bucket()
    return settings.AWS_STORAGE_BUCKET_NAME
