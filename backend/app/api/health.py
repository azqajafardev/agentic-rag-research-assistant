"""Health check endpoint.

Every field reflects a real, just-performed check - never a hardcoded
"ready" value. A failing dependency degrades its own field to "unavailable"
without taking down the endpoint itself, so /api/health stays useful for
diagnosing exactly what's wrong.
"""

import logging

from fastapi import APIRouter, Depends

from app.api.deps import get_vector_service
from app.core.config import Settings, get_settings
from app.db.database import get_connection
from app.schemas.health import HealthResponse

logger = logging.getLogger("evidencerag")

router = APIRouter(prefix="/api", tags=["health"])


def _check_database(settings: Settings) -> str:
    try:
        with get_connection(settings.database_path) as conn:
            conn.execute("SELECT 1")
        return "connected"
    except Exception:
        logger.exception("health_database_check_failed")
        return "unavailable"


def _check_vector_db(settings: Settings) -> str:
    try:
        get_vector_service(settings).count()
        return "connected"
    except Exception:
        logger.exception("health_vector_db_check_failed")
        return "unavailable"


@router.get("/health", response_model=HealthResponse, summary="Check backend health")
def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    database_status = _check_database(settings)
    vector_db_status = _check_vector_db(settings)
    overall = (
        "ok" if database_status == "connected" and vector_db_status == "connected" else "degraded"
    )

    return HealthResponse(
        status=overall,
        backend="connected",
        database=database_status,
        vector_db=vector_db_status,
    )
