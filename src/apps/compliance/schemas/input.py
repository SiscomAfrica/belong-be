from __future__ import annotations

from uuid import UUID

from ninja import Schema
from pydantic import Field


class RecordConsentIn(Schema):
    consent_version_id: UUID = Field(description="UUID of the consent version being accepted")
