from fastapi import APIRouter

from app.repositories.ops_repository import get_delay_summary


router = APIRouter(prefix="/ops", tags=["operations"])


@router.get("/delay-summary")
def read_delay_summary():
    return get_delay_summary()