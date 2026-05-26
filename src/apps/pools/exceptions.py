from __future__ import annotations

from apps.common.exceptions import NotFoundError


class PoolNotFoundError(NotFoundError):
    code = "POOL_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Pool not found.")
