from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.common.services.s3 import generate_presigned_download


class FundHoldingOut(Schema):
    id: UUID = Field(description="Holding identifier")
    name: str = Field(description="Holding company name")
    logo_url: str = Field(description="Presigned logo URL")
    position: int = Field(description="Display order position")

    @staticmethod
    def resolve_logo_url(obj: object) -> str:
        image = getattr(obj, "logo_image", None)
        if image and getattr(image, "name", ""):
            return generate_presigned_download(file_key=image.name)["download_url"]
        url = getattr(obj, "logo_url", "")
        if not url or url.startswith("http"):
            return url or ""
        return generate_presigned_download(file_key=url)["download_url"]
