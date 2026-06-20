from __future__ import annotations

import uuid

import boto3
from django.conf import settings

UPLOAD_EXPIRY = 900  # 15 minutes
DOWNLOAD_EXPIRY = 3600  # 1 hour


def _get_s3_client():  # noqa: ANN202
    return boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def generate_presigned_upload(
    *, folder: str, filename: str, content_type: str,
) -> dict:
    file_key = f"{folder}/{uuid.uuid4()}/{filename}"
    client = _get_s3_client()
    upload_url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
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
    client = _get_s3_client()
    download_url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": file_key,
        },
        ExpiresIn=DOWNLOAD_EXPIRY,
    )
    return {
        "download_url": download_url,
        "expires_in": DOWNLOAD_EXPIRY,
    }
