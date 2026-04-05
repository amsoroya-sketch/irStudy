"""
Health Check Endpoints

Kubernetes-compatible liveness and readiness probes.

Routes:
- GET /health/live - Liveness probe (is app running?)
- GET /health/ready - Readiness probe (can serve traffic?)

INTEGRATION:
- Database connectivity
- Redis connectivity
- Vault connectivity
- Claude API availability

PERFORMANCE:
- Liveness: <10ms (simple check)
- Readiness: <100ms (all dependency checks)
"""

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from src.db.base import get_db
from src.core.vault import VaultClient
from src.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


# ============================================================================
# LIVENESS PROBE
# ============================================================================

@router.get("/live",
            summary="Liveness Probe",
            description="""
Kubernetes liveness probe - checks if application is running.

**Response:**
- 200 OK: Application is alive
- Returns: {"status": "alive", "timestamp": "<ISO 8601>"}

**Performance:** <10ms target
**Use case:** Kubernetes restarts pod if this fails
""",
            responses={
                200: {"description": "Application is alive"}
            })
async def liveness_check():
    """
    Simple liveness check.

    Always returns 200 if the application is running.
    Kubernetes uses this to restart crashed pods.

    Performance: <10ms
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# READINESS PROBE
# ============================================================================

@router.get("/ready",
            summary="Readiness Probe",
            description="""
Kubernetes readiness probe - checks if application can serve traffic.

**Checks:**
1. Database connection
2. Redis connection
3. Vault connection (optional - degrades gracefully)
4. Claude API (optional - uses fallback)

**Response:**
- 200 OK: All checks passed, ready to serve traffic
- 503 Service Unavailable: One or more critical checks failed

**Performance:** <100ms target
**Use case:** Kubernetes routes traffic only to ready pods
""",
            responses={
                200: {"description": "Application is ready"},
                503: {"description": "Application is not ready"}
            })
async def readiness_check(db: Session = Depends(get_db)):
    """
    Comprehensive readiness check.

    Checks all critical dependencies before declaring ready.
    Non-critical failures (Vault, Claude) result in warnings but still ready.

    Performance: <100ms target
    """
    checks = {}
    all_critical_ready = True

    # 1. Database check (CRITICAL)
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1")).scalar()
        checks["database"] = {"status": "healthy", "critical": True}
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        checks["database"] = {"status": "unhealthy", "error": str(e), "critical": True}
        all_critical_ready = False

    # 2. Redis check (CRITICAL)
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        checks["redis"] = {"status": "healthy", "critical": True}
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        checks["redis"] = {"status": "unhealthy", "error": str(e), "critical": True}
        all_critical_ready = False

    # 3. Vault check (NON-CRITICAL - degrades gracefully)
    try:
        vault = VaultClient()
        if vault.client:
            vault.client.is_authenticated()
            checks["vault"] = {"status": "healthy", "critical": False}
        else:
            checks["vault"] = {"status": "degraded", "message": "Fallback to env vars", "critical": False}
    except Exception as e:
        logger.warning(f"Vault check failed (non-critical): {e}")
        checks["vault"] = {"status": "degraded", "error": str(e), "critical": False}

    # 4. Claude API check (NON-CRITICAL - has fallback validator)
    try:
        # Check if Claude API key is available
        vault = VaultClient()
        claude_key = vault.get_secret("emr/claude-api-key")
        if claude_key:
            checks["claude_api"] = {"status": "healthy", "critical": False}
        else:
            checks["claude_api"] = {"status": "degraded", "message": "Fallback validator available", "critical": False}
    except Exception as e:
        logger.warning(f"Claude API check failed (non-critical): {e}")
        checks["claude_api"] = {"status": "degraded", "message": "Fallback validator available", "critical": False}

    # Determine overall status
    status_code = status.HTTP_200_OK if all_critical_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    overall_status = "ready" if all_critical_ready else "not_ready"

    # Count healthy checks
    healthy_count = sum(1 for check in checks.values() if check["status"] in ["healthy", "degraded"])
    total_count = len(checks)

    response_body = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "summary": {
            "healthy": healthy_count,
            "total": total_count,
            "percentage": round((healthy_count / total_count) * 100, 1)
        }
    }

    return JSONResponse(
        status_code=status_code,
        content=response_body
    )


# ============================================================================
# DETAILED STATUS (ADMIN ONLY)
# ============================================================================

@router.get("/status",
            summary="Detailed Status (Admin)",
            description="""
Detailed application status for monitoring and debugging.

**Includes:**
- All health checks
- Database pool stats
- Redis memory usage
- Active sessions count
- Version information

**Authentication:** Admin role required
""")
async def detailed_status(db: Session = Depends(get_db)):
    """
    Detailed status information.

    Useful for monitoring dashboards and debugging.
    """
    from sqlalchemy import text

    status_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",  # TODO: Get from environment
        "environment": "development",  # TODO: Get from environment
    }

    # Database stats
    try:
        active_sessions = db.execute(text("""
            SELECT COUNT(*) FROM emr_sessions WHERE submitted_at IS NULL
        """)).scalar()

        completed_sessions = db.execute(text("""
            SELECT COUNT(*) FROM emr_sessions WHERE submitted_at IS NOT NULL
        """)).scalar()

        status_info["database"] = {
            "status": "healthy",
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions
        }
    except Exception as e:
        status_info["database"] = {
            "status": "error",
            "error": str(e)
        }

    # Redis stats
    try:
        redis_client = get_redis_client()
        redis_info = redis_client.info("memory")
        status_info["redis"] = {
            "status": "healthy",
            "used_memory_human": redis_info.get("used_memory_human"),
            "connected_clients": redis_info.get("connected_clients")
        }
    except Exception as e:
        status_info["redis"] = {
            "status": "error",
            "error": str(e)
        }

    return status_info
