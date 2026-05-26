from fastapi import APIRouter, Query

from app.repositories.audit_repository import get_audit_runs


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/runs")
def read_audit_runs(limit: int = Query(default=20, ge=1, le=100)):
    return {
        "limit": limit,
        "results": get_audit_runs(limit),
    }