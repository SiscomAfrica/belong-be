from __future__ import annotations

from django.db import connection
from ninja import Router, Schema

health_router = Router(auth=None)


class HealthOut(Schema):
    status: str
    db: str


@health_router.get("/", response=HealthOut)
def health_check(request):  # noqa: ANN001, ANN201
    """Check API and database health. Returns 200 if healthy, 503 otherwise."""
    db_status = "ok"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:  # noqa: BLE001
        db_status = "error"

    status = "healthy" if db_status == "ok" else "unhealthy"
    return {"status": status, "db": db_status}
