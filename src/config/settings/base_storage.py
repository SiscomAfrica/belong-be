from __future__ import annotations

import environ

env = environ.Env()

# AWS S3 storage settings
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_REGION_NAME = env("AWS_REGION", default="us-east-1")
# Stripped because a stray space in the .env value becomes part of the
# bucket name in every request path and signature, and the failure surfaces
# as a baffling 404 rather than a config error.
AWS_STORAGE_BUCKET_NAME = env("AWS_BUCKET", default="").strip()
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
# R2 accepts SigV4 only.
AWS_S3_SIGNATURE_VERSION = "s3v4"
# Public bucket: fund and playlist heroes, holding logos, profile photos.
# Served from a Cloudflare domain under permanent, cacheable URLs. The
# private bucket above keeps KYC documents and selfies.
PUBLIC_MEDIA_BUCKET = env("PUBLIC_MEDIA_BUCKET", default="belong-media").strip()
PUBLIC_MEDIA_URL = env(
    "PUBLIC_MEDIA_URL", default="https://media.belong.club",
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
