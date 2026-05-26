from datetime import datetime

from app.database import db
from app.repositories.ops_repository import (
    get_cancellations_by_airport,
    get_delay_summary,
    get_passenger_impact_summary,
    get_top_delayed_routes,
)


def _build_snapshot_id() -> str:
    date_key = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"snapshot_{date_key}_"
    today_count = db.ops_metrics_snapshots.count_documents({"snapshot_id": {"$regex": f"^{prefix}"}})
    return f"{prefix}{today_count + 1:03d}"


def build_analytics_snapshots():
    started_at = datetime.utcnow()

    delay_summary = get_delay_summary()
    top_delayed_routes = get_top_delayed_routes(limit=20, min_flights=5).get("results", [])
    cancellations_by_airport = get_cancellations_by_airport(limit=20, min_flights=10).get("results", [])
    passenger_impact_summary = get_passenger_impact_summary()

    total_flights = delay_summary.get("total_flights", 0)
    delayed_flights = delay_summary.get("delayed_flights", 0)
    cancelled_flights = delay_summary.get("cancelled_flights", 0)

    if total_flights:
        delay_rate = round((delayed_flights / total_flights) * 100, 2)
        cancellation_rate = round((cancelled_flights / total_flights) * 100, 2)
    else:
        delay_rate = 0
        cancellation_rate = 0

    snapshot_document = {
        "snapshot_id": _build_snapshot_id(),
        "created_at": datetime.utcnow(),
        "source": "mongodb_operational_collections",
        "metrics": {
            "total_flights": total_flights,
            "delayed_flights": delayed_flights,
            "cancelled_flights": cancelled_flights,
            "delay_rate": delay_rate,
            "cancellation_rate": cancellation_rate,
            "average_departure_delay": delay_summary.get("average_departure_delay", 0),
            "average_arrival_delay": delay_summary.get("average_arrival_delay", 0),
            "max_departure_delay": delay_summary.get("max_departure_delay", 0),
        },
        "top_delayed_routes": top_delayed_routes,
        "cancellations_by_airport": cancellations_by_airport,
        "passenger_impact_summary": passenger_impact_summary,
    }

    db.ops_metrics_snapshots.insert_one(snapshot_document)

    finished_at = datetime.utcnow()
    db.audit_runs.insert_one({
        "process_name": "build_analytics_snapshots",
        "status": "SUCCESS",
        "started_at": started_at,
        "finished_at": finished_at,
        "records_processed": total_flights,
        "records_inserted": 1,
        "errors": [],
    })

    print(f"Created snapshot: {snapshot_document['snapshot_id']}")
    print(f"Generated analytics snapshot in {finished_at - started_at}")


if __name__ == "__main__":
    build_analytics_snapshots()
