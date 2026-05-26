from __future__ import annotations

from uuid import UUID

from ninja import Schema


class RecordConsentIn(Schema):
    consent_version_id: UUID
