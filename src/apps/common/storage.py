from __future__ import annotations

import os

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

from apps.common.services.media_routing import public_media_bucket, public_media_url


class PublicMediaStorage(S3Boto3Storage):
    """Upload target for catalogue art, which is world-readable by design.

    Without this the two halves disagree: an admin upload goes to the default
    (private) bucket while the serialiser hands out a media.belong.club URL for
    it, so every newly uploaded image 404s. Pointing the field here puts the
    object where the URL already claims it is.

    Falls back to the private bucket while PUBLIC_MEDIA_BUCKET is unset, so a
    half-finished setup keeps working on signed URLs.
    """

    # These objects are public; a signature on the URL would only defeat
    # caching, which is the entire point of putting them here.
    querystring_auth = False

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault(
            "bucket_name",
            public_media_bucket() or settings.AWS_STORAGE_BUCKET_NAME,
        )
        domain = public_media_url()
        if domain:
            kwargs.setdefault("custom_domain", domain.split("://")[-1])
        super().__init__(**kwargs)


def hero_image_upload_path(instance, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    model_label = instance._meta.model_name
    return f"hero_images/{model_label}s/{instance.pk}{ext}"


def holding_logo_upload_path(instance, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return f"holding_logos/{instance.fund_id}/{instance.pk}{ext}"
