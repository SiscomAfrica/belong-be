from __future__ import annotations

import environ

env = environ.Env()

# AWS S3 storage settings
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_S3_REGION_NAME = env("AWS_REGION", default="us-east-1")
AWS_STORAGE_BUCKET_NAME = env("AWS_BUCKET", default="")
AWS_S3_CUSTOM_DOMAIN = env("S3_URL", default="")

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/" if AWS_S3_CUSTOM_DOMAIN else "/media/"
