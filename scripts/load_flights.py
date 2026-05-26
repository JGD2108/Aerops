
import csv 
import time
from datetime import datetime
from io import StringIO

from app.database import db
from app.storage_client import get_storage_client
from pymongo.errors import BulkWriteError, OperationFailure


def _insert_in_batches_with_retry(collection, documents, batch_size=100, max_retries=8):
    inserted = 0
    for start in range(0, len(documents), batch_size):
        batch = documents[start : start + batch_size]
        attempt = 0
        while True:
            try:
                collection.insert_many(batch, ordered=False)
                inserted += len(batch)
                break
            except BulkWriteError as exc:
                errors = exc.details.get("writeErrors", [])
                is_throttled = bool(errors) and all(err.get("code") == 16500 for err in errors)
                if not is_throttled or attempt >= max_retries:
                    raise
                time.sleep(min(2**attempt, 30))
                attempt += 1
            except OperationFailure as exc:
                if exc.code != 16500 or attempt >= max_retries:
                    raise
                time.sleep(min(2**attempt, 30))
                attempt += 1


def to_bool(value):
    return str(value).lower() == "true"
def load_flights():
    start_time = datetime.utcnow()
    db.flights.delete_many({})
    storage_client = get_storage_client()
    csv_text = storage_client.read_text("processed", "flights_processed.csv")
    reader = csv.DictReader(StringIO(csv_text))
    flights = []
    for row in reader:
        row['departure_delay_minutes'] = float(row['departure_delay_minutes'])
        row['arrival_delay_minutes'] = float(row['arrival_delay_minutes'])
        row['distance'] = float(row['distance'])
        row['cancelled'] = to_bool(row['cancelled'])
        row['diverted'] = to_bool(row['diverted'])
        
        flights.append(row)
    if flights:
        _insert_in_batches_with_retry(db.flights, flights, batch_size=50)
    end_time = datetime.utcnow()
    print(f"Inserted {len(flights)} flights")
    print(f"Loaded flights in {end_time - start_time}")
    db.audit_runs.insert_one({
        "process_name": "load_flights",
        "status": "SUCCESS",
        "started_at": start_time,
        "finished_at": end_time,
        "records_processed": len(flights),
        "records_inserted": len(flights),
        "errors": []
    })
    
if __name__ == "__main__":
    load_flights()
