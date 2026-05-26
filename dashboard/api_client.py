import os
from typing import Any, Dict

import requests


API_BASE_URL = os.getenv("AEROOPS_API_BASE_URL", "http://localhost:8000")


def _get(path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def get_delay_summary() -> Dict[str, Any]:
    return _get("/ops/delay-summary")


def get_top_delayed_routes(limit: int = 10, min_flights: int = 5) -> Dict[str, Any]:
    return _get(
        "/ops/top-delayed-routes",
        params={"limit": limit, "min_flights": min_flights},
    )


def get_cancellations_by_airport(
    limit: int = 20,
    min_flights: int = 10,
) -> Dict[str, Any]:
    return _get(
        "/ops/cancellations-by-airport",
        params={"limit": limit, "min_flights": min_flights},
    )


def get_passenger_impact_summary() -> Dict[str, Any]:
    return _get("/ops/passenger-impact-summary")


def get_audit_runs(limit: int = 20) -> Dict[str, Any]:
    return _get("/audit/runs", params={"limit": limit})


def get_latest_metrics_snapshot() -> Dict[str, Any]:
    return _get("/ops/metrics-snapshots/latest")


def get_metrics_snapshots(limit: int = 20) -> Dict[str, Any]:
    return _get("/ops/metrics-snapshots", params={"limit": limit})
