from datetime import datetime

from pymongo import ASCENDING, DESCENDING

from app.database import db


def _remove_duplicates_by_field(collection, field_name):
    pipeline = [
        {"$match": {field_name: {"$nin": [None, ""]}}},
        {"$group": {"_id": f"${field_name}", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
    ]
    duplicates = list(collection.aggregate(pipeline, allowDiskUse=True))
    removed = 0
    for doc in duplicates:
        ids = doc.get("ids", [])
        if len(ids) > 1:
            delete_ids = ids[1:]
            result = collection.delete_many({"_id": {"$in": delete_ids}})
            removed += result.deleted_count
    return removed


def create_indexes():
    started_at = datetime.utcnow()

    # Ensure unique index creation is idempotent in Cosmos/Mongo across reruns.
    _remove_duplicates_by_field(db.flights, "flight_id")
    _remove_duplicates_by_field(db.ops_metrics_snapshots, "snapshot_id")

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
