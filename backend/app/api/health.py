from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Liveness probe used by CI, Docker healthcheck, and load balancers."""
    return {"status": "ok"}