from fastapi import APIRouter, HTTPException, Query

from app.repositories.flights_repository import (
    get_flight_by_id,
    get_flights_by_origin,
    get_flights_by_status,
)


router = APIRouter(prefix="/flights", tags=["flights"])


@router.get("/{flight_id}")
def read_flight(flight_id: str):
    flight = get_flight_by_id(flight_id)

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    return flight


@router.get("/status/{status}")
def read_flights_by_status(status: str, limit: int = Query(default=50, ge=1, le=200)):
    return {
        "status": status.upper(),
        "limit": limit,
        "results": get_flights_by_status(status, limit),
    }


@router.get("/origin/{origin}")
def read_flights_by_origin(origin: str, limit: int = Query(default=50, ge=1, le=200)):
    return {
        "origin": origin.upper(),
        "limit": limit,
        "results": get_flights_by_origin(origin, limit),
    }