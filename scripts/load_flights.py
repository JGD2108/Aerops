
import csv 
import re
import time
from datetime import datetime
from io import StringIO

from app.database import db
from app.storage_client import get_storage_client
from pymongo.errors import DuplicateKeyError, OperationFailure, WriteError


def _retry_sleep_seconds(exc, attempt):
    message = str(exc)
    match = re.search(r"RetryAfterMs=(\d+)", message)
    if match:
        return max(int(match.group(1)) / 1000.0, 0.05)
    return min(2**attempt, 30)


def _insert_one_by_one_with_retry(collection, documents, max_retries=10):
    inserted = 0
    for doc in documents:
        attempt = 0
        while True:
            try:
                collection.insert_one(doc)
                inserted += 1
                break
            except DuplicateKeyError:
                break
            except OperationFailure as exc:
                if exc.code != 16500 or attempt >= max_retries:
                    raise
                time.sleep(_retry_sleep_seconds(exc, attempt))
                attempt += 1
            except WriteError as exc:
                if exc.code != 16500 or attempt >= max_retries:
                    raise
                time.sleep(_retry_sleep_seconds(exc, attempt))
                attempt += 1
    return inserted


def _delete_many_with_retry(collection, query, max_retries=10):
    attempt = 0
    while True:
        try:
            collection.delete_many(query)
            return
        except (WriteError, OperationFailure) as exc:
            if getattr(exc, "code", None) != 16500 or attempt >= max_retries:
                raise
            time.sleep(_retry_sleep_seconds(exc, attempt))
            attempt += 1


def to_bool(value):
    return str(value).lower() == "true"
def load_flights():
    start_time = datetime.utcnow()
    _delete_many_with_retry(db.flights, {})
    storage_client = get_storage_client()
    csv_text = storage_client.read_text("processed", "flights_processed.csv")
    reader = csv.DictReader(StringIO(csv_text))
    flights = []
    seen_flight_ids = set()
    for row in reader:
        flight_id = row.get("flight_id")
        if flight_id in seen_flight_ids:
            continue
        seen_flight_ids.add(flight_id)
        row['departure_delay_minutes'] = float(row['departure_delay_minutes'])
        row['arrival_delay_minutes'] = float(row['arrival_delay_minutes'])
        row['distance'] = float(row['distance'])
        row['cancelled'] = to_bool(row['cancelled'])
        row['diverted'] = to_bool(row['diverted'])
        
        flights.append(row)
    if flights:
        inserted = _insert_one_by_one_with_retry(db.flights, flights)
    else:
        inserted = 0
    end_time = datetime.utcnow()
    print(f"Inserted {inserted} flights")
    print(f"Loaded flights in {end_time - start_time}")
    db.audit_runs.insert_one({
        "process_name": "load_flights",
        "status": "SUCCESS",
        "started_at": start_time,
        "finished_at": end_time,
        "records_processed": len(flights),
        "records_inserted": inserted,
        "errors": []
    })
    
if __name__ == "__main__":
    load_flights()
