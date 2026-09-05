from __future__ import annotations

import uuid
from functools import lru_cache

import boto3
from botocore.config import Config
from django.conf import settings

from apps.common.exceptions import ValidationError
from apps.common.services.media_routing import (
    UPLOAD_FOLDERS,
    bucket_for,
    is_public,
    is_uploadable,
    public_media_url,
)


def _client_config() -> Config:
    configured = getattr(settings, "AWS_S3_CLIENT_CONFIG", None)
    if configured is not None:
        return configured
    return Config(
        signature_version="s3v4",
        request_checksum_calculation="when_required",
        response_checksum_validation="when_supported",
    )


UPLOAD_EXPIRY = 900  # 15 minutes
DOWNLOAD_EXPIRY = 3600  # 1 hour


@lru_cache(maxsize=1)
def get_s3_client():
    """One client per process.

    Constructing a boto3 client resolves credentials and loads service metadata
    from disk. Serialising a fund list built one client per image, paying that
    cost once per image before a single byte was signed.

    Cached on settings, so a test overriding any AWS_* value must call
    `get_s3_client.cache_clear()`.
    """
    return boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        # Objects live in Cloudflare R2. Without an explicit endpoint every
        # signature is generated for AWS S3 instead, producing URLs that point
        # at a bucket host which does not exist.
        endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None) or None,
        # Shared with django-storages so both clients speak to R2 the same
        # way. Carries the SigV4 pin and, critically, the checksum settings
        # without which boto3 1.36+ sends a trailer checksum R2 rejects.
        config=_client_config(),
    )


def generate_presigned_upload(
    *,
    folder: str,
    filename: str,
    content_type: str,
) -> dict:
    if not is_uploadable(folder):
        # The folder decides the bucket, so an unchecked value from the client
        # is a way to write into public storage.
        allowed = ", ".join(sorted(UPLOAD_FOLDERS))
        raise ValidationError(f"Unknown upload folder. Expected one of: {allowed}.")

    file_key = f"{folder}/{uuid.uuid4()}/{filename}"
    upload_url = get_s3_client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket_for(file_key),
            "Key": file_key,
            "ContentType": content_type,
        },
        ExpiresIn=UPLOAD_EXPIRY,
    )
    return {
        "upload_url": upload_url,
        "file_key": file_key,
        "expires_in": UPLOAD_EXPIRY,
    }


def generate_presigned_download(*, file_key: str) -> dict:
    """A URL for a stored object.

    Public folders get a permanent CDN URL rather than a signature. Signing
    them was what stopped every cache from ever hitting: the query string
    changed on every response, so Cloudflare, the OS and the app's own image
    cache each saw a brand-new image and re-downloaded the whole catalogue.
    """
    if is_public(file_key) and public_media_url():
        return {
            "download_url": f"{public_media_url()}/{file_key}",
            "expires_in": DOWNLOAD_EXPIRY,
        }

    download_url = get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_for(file_key), "Key": file_key},
        ExpiresIn=DOWNLOAD_EXPIRY,
    )
    return {
        "download_url": download_url,
        "expires_in": DOWNLOAD_EXPIRY,
    }
