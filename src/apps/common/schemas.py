from __future__ import annotations

from ninja import Schema


class ErrorDetail(Schema):
    code: str
    message: str
    details: dict = {}


class ErrorOut(Schema):
    error: ErrorDetail
