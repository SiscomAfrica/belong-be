from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.funds.schemas.output_playlist import PlaylistOut


class ProfileTemplateOut(Schema):
    id: UUID = Field(description="Profile template identifier")
    investor_type: str = Field(description="Investor type enum value")
    name: str = Field(description="Profile display name")
    slug: str = Field(description="URL-safe profile slug")
    accent: str = Field(description="Title accent text")
    badge_label: str = Field(description="Badge label text")
    description: str = Field(description="Profile description")
    section_title: str = Field(description="Jams section heading")
    section_action: str = Field(description="Jams section action label")
    playlist: PlaylistOut | None = Field(description="Linked playlist with funds")
    is_active: bool = Field(description="Whether this template is active")
    position: int = Field(description="Display order")


class ProfileTemplateListOut(Schema):
    items: list[ProfileTemplateOut] = Field(description="List of profile templates")
    count: int = Field(description="Total number of templates")
