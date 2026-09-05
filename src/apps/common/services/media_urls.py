from __future__ import annotations

from apps.common.services.s3 import generate_presigned_download


def catalogue_image_url(*, file_key: str) -> str:
    """URL for public catalogue art — fund heroes, playlist heroes, logos.

    Routing lives in `generate_presigned_download`, which returns a permanent
    CDN URL for public folders and a signed one for everything else. This wraps
    it with the two cases a stored key can also be in: absent, or already an
    absolute URL left over from seed data.
    """
    if not file_key:
        return ""
    if file_key.startswith("http"):
        return file_key
    return generate_presigned_download(file_key=file_key)["download_url"]


def catalogue_image_field_url(*, image: object, fallback_key: str) -> str:
    """Resolve from an uploaded file if there is one, else from a stored key.

    Every catalogue model carries both an ImageField and a legacy URL column,
    and this resolution was copied into three schemas and the admin. Keeping it
    in one place is what stops them drifting apart again.
    """
    name = getattr(image, "name", "") if image else ""
    return catalogue_image_url(file_key=name or fallback_key or "")
