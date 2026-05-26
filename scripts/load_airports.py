import csv 
import re
import time
from datetime import datetime
from io import StringIO

from app.database import db
from app.storage_client import get_storage_client
from pymongo.errors import OperationFailure, WriteError


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
            except (WriteError, OperationFailure) as exc:
                if getattr(exc, "code", None) != 16500 or attempt >= max_retries:
                    raise
                time.sleep(_retry_sleep_seconds(exc, attempt))
                attempt += 1
    return inserted

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
    inserted = _insert_one_by_one_with_retry(db.airports, airports)
    end_time = datetime.utcnow()
    print(f"Inserted {inserted} airports")
    print(f"Loaded airports in {end_time - start_time}")
    db.audit_runs.insert_one({
        "process_name": "load_airports",
        "status": "SUCCESS",
        "started_at": start_time,
        "ended_at": end_time,
        "records_processed": len(airports),
        "records_inserted": inserted,
        "errors": []
    })

if __name__ == "__main__":
    load_airports()
