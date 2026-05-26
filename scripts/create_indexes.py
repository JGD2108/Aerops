from datetime import datetime

from pymongo import ASCENDING, DESCENDING

from app.database import db


def create_indexes():
    started_at = datetime.utcnow()

    # flights indexes
    db.flights.create_index([("flight_id", ASCENDING)], unique=True)
    db.flights.create_index([("origin", ASCENDING), ("flight_date", ASCENDING)])
    db.flights.create_index([("destination", ASCENDING), ("flight_date", ASCENDING)])
    db.flights.create_index([("status", ASCENDING), ("flight_date", ASCENDING)])
    db.flights.create_index([("departure_delay_minutes", DESCENDING)])

    # flight_events indexes
    db.flight_events.create_index([("flight_id", ASCENDING), ("timestamp", DESCENDING)])

    # passenger_itineraries indexes
    db.passenger_itineraries.create_index([("flights", ASCENDING)])

    # audit_runs indexes
    db.audit_runs.create_index([("started_at", DESCENDING)])

    # ops_metrics_snapshots indexes
    db.ops_metrics_snapshots.create_index([("created_at", DESCENDING)])
    db.ops_metrics_snapshots.create_index([("snapshot_id", ASCENDING)], unique=True)

    finished_at = datetime.utcnow()

    db.audit_runs.insert_one({
        "process_name": "create_indexes",
        "status": "SUCCESS",
        "started_at": started_at,
        "finished_at": finished_at,
        "records_processed": 0,
        "records_inserted": 0,
        "errors": []
    })

    print("Indexes created successfully")

    print("\nFlights indexes:")
    for index in db.flights.list_indexes():
        print(index)

    print("\nFlight events indexes:")
    for index in db.flight_events.list_indexes():
        print(index)

    print("\nPassenger itineraries indexes:")
    for index in db.passenger_itineraries.list_indexes():
        print(index)

    print("\nAudit runs indexes:")
    for index in db.audit_runs.list_indexes():
        print(index)

    print("\nOps metrics snapshots indexes:")
    for index in db.ops_metrics_snapshots.list_indexes():
        print(index)


if __name__ == "__main__":
    create_indexes()
