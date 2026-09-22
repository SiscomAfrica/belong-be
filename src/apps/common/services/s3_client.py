from __future__ import annotations

from functools import lru_cache

import boto3
from botocore.config import Config
from django.conf import settings

UPLOAD_EXPIRY = 900  # 15 minutes
DOWNLOAD_EXPIRY = 3600  # 1 hour


def _client_config() -> Config:
    configured = getattr(settings, "AWS_S3_CLIENT_CONFIG", None)
    if configured is not None:
        return configured
    return Config(
        signature_version="s3v4",
        request_checksum_calculation="when_required",
        response_checksum_validation="when_supported",
    )


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
