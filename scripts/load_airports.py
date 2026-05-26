import csv 
import time
from datetime import datetime
from io import StringIO

from app.database import db
from app.storage_client import get_storage_client
from pymongo.errors import BulkWriteError, OperationFailure, WriteError


def _insert_in_batches_with_retry(collection, documents, batch_size=50, max_retries=8):
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
            except WriteError as exc:
                if exc.code != 16500 or attempt >= max_retries:
                    raise
                time.sleep(min(2**attempt, 30))
                attempt += 1

def load_airports():
    start_time = datetime.utcnow()
    db.airports.delete_many({})
    storage_client = get_storage_client()
    # convert latitude and longitude in float 
    csv_text = storage_client.read_text("processed", "airports_processed.csv")
    reader = csv.DictReader(StringIO(csv_text))
    airports = []
    for row in reader:
        row['latitude'] = float(row['latitude'])
        row['longitude'] = float(row['longitude'])
        airports.append(row)
    _insert_in_batches_with_retry(db.airports, airports, batch_size=5)
    end_time = datetime.utcnow()
    print(f"Inserted {len(airports)} airports")
    print(f"Loaded airports in {end_time - start_time}")
    db.audit_runs.insert_one({
        "process_name": "load_airports",
        "status": "SUCCESS",
        "started_at": start_time,
        "ended_at": end_time,
        "records_processed": len(airports),
        "records_inserted": len(airports),
        "errors": []
    })

if __name__ == "__main__":
    load_airports()
