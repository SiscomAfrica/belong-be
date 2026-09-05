from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.common.services.media_urls import catalogue_image_field_url


class FundHoldingOut(Schema):
    id: UUID = Field(description="Holding identifier")
    name: str = Field(description="Holding company name")
    logo_url: str = Field(description="Cacheable logo URL")
    position: int = Field(description="Display order position")

    @staticmethod
    def resolve_logo_url(obj: object) -> str:
        return catalogue_image_field_url(
            image=getattr(obj, "logo_image", None),
            fallback_key=getattr(obj, "logo_url", ""),
        )
