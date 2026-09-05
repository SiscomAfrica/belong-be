from __future__ import annotations

import environ
from botocore.config import Config

env = environ.Env()

# Storage is Cloudflare R2 throughout — there is no AWS S3 anywhere in this
# system. The AWS_* names are kept only because django-storages and boto3
# read those keys; treat every one of them as "R2".
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
# R2 has no regions; "auto" is the literal value it expects. The region is
# part of the SigV4 signing scope, so an AWS region name here produces
# SignatureDoesNotMatch rather than anything that names the real problem.
AWS_S3_REGION_NAME = env("AWS_REGION", default="auto")
# Stripped because a stray space in the .env value becomes part of the
# bucket name in every request path and signature, and the failure surfaces
# as a baffling 404 rather than a config error.
AWS_STORAGE_BUCKET_NAME = env("AWS_BUCKET", default="").strip()
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
# R2 accepts SigV4 only.
AWS_S3_SIGNATURE_VERSION = "s3v4"

# boto3 1.36+ defaults to sending a CRC32 trailer checksum, which turns an
# upload into an aws-chunked streaming request with
# X-Amz-Content-SHA256: STREAMING-UNSIGNED-PAYLOAD-TRAILER. R2 does not
# implement trailer checksums and rejects those, so every direct upload —
# admin image uploads and generated variants alike — fails without this.
# "when_required" falls back to an ordinary signed payload.
#
# django-storages reads this key for the client it builds itself; our own
# client in apps/common/services/s3.py applies the same settings.
AWS_S3_CLIENT_CONFIG = Config(
    signature_version=AWS_S3_SIGNATURE_VERSION,
    request_checksum_calculation="when_required",
    response_checksum_validation="when_supported",
)
# Public bucket: fund and playlist heroes, holding logos, profile photos.
# Served from a Cloudflare domain under permanent, cacheable URLs. The
# private bucket above keeps KYC documents and selfies.
PUBLIC_MEDIA_BUCKET = env("PUBLIC_MEDIA_BUCKET", default="belong-media").strip()
PUBLIC_MEDIA_URL = env(
    "PUBLIC_MEDIA_URL",
    default="https://media.belong.club",
).rstrip("/")
_s3_url = env("S3_URL", default="")
AWS_S3_CUSTOM_DOMAIN = _s3_url.replace("https://", "").replace("http://", "").rstrip("/")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/" if AWS_S3_CUSTOM_DOMAIN else "/media/"
