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
        key = getattr(obj, "logo_url", "")
        if not key or key.startswith("http"):
            return key or ""
        return generate_presigned_download(file_key=key)["download_url"]
