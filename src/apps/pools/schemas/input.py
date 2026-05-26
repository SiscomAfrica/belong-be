from __future__ import annotations

from decimal import Decimal

from ninja import Schema
from pydantic import Field


class PoolNavUpdateIn(Schema):
    nav_per_unit: Decimal = Field(gt=0)
