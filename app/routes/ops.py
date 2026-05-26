from fastapi import APIRouter, Query

from app.repositories.ops_repository import (
    get_cancellations_by_airport,
    get_delay_summary,
    get_passenger_impact_summary,
    get_top_delayed_routes,
)


router = APIRouter(prefix="/ops", tags=["operations"])


@router.get("/delay-summary")
def read_delay_summary():
    return get_delay_summary()


@router.get("/top-delayed-routes")
def read_top_delayed_routes(
    limit: int = Query(default=10, ge=1, le=100),
    min_flights: int = Query(default=5, ge=1, le=100000),
):
    return get_top_delayed_routes(limit=limit, min_flights=min_flights)


@router.get("/cancellations-by-airport")
def read_cancellations_by_airport(
    limit: int = Query(default=20, ge=1, le=200),
    min_flights: int = Query(default=10, ge=1, le=100000),
):
    return get_cancellations_by_airport(limit=limit, min_flights=min_flights)


@router.get("/passenger-impact-summary")
def read_passenger_impact_summary():
    return get_passenger_impact_summary()
