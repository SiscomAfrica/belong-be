from __future__ import annotations

from ninja import Schema


class PresignedUploadIn(Schema):
    folder: str
    filename: str
    content_type: str


class PresignedUploadOut(Schema):
    upload_url: str
    file_key: str
    expires_in: int


class DownloadUrlIn(Schema):
    file_key: str


class DownloadUrlOut(Schema):
    download_url: str
    expires_in: int
