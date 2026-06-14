from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field

from apps.funds.schemas.output import FundOut


class PlaylistFundOut(Schema):
    fund: FundOut = Field(description="Fund details")
    position: int = Field(description="Display order within the playlist")
    returns_label: str = Field(description="Label for the return metric shown on the card")


class PlaylistOut(Schema):
    id: UUID = Field(description="Playlist identifier")
    name: str = Field(description="Playlist display name")
    slug: str = Field(description="URL-safe playlist slug")
    description: str = Field(description="Playlist description")
    hero_image_url: str = Field(description="Playlist hero image URL")
    funds: list[PlaylistFundOut] = Field(description="Ordered funds in this playlist")

    @staticmethod
    def resolve_funds(obj):  # noqa: ANN001, ANN205
        return [
            {"fund": pf.fund, "position": pf.position, "returns_label": pf.returns_label}
            for pf in obj.playlist_funds.all()
        ]


class PlaylistListOut(Schema):
    items: list[PlaylistOut] = Field(description="List of playlists")
    count: int = Field(description="Total number of playlists")
