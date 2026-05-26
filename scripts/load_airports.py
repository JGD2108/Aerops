import csv 
from datetime import datetime
from io import StringIO

from app.database import db
from app.storage_client import get_storage_client
from scripts.cosmos_retry import run_with_cosmos_retry


def _upsert_one_by_one_with_retry(collection, documents):
    processed = 0
    inserted = 0
    for doc in documents:
        processed += 1
        result = run_with_cosmos_retry(
            lambda: collection.replace_one({"iata_code": doc["iata_code"]}, doc, upsert=True)
        )
        if result.upserted_id is not None:
            inserted += 1
    return processed, inserted


def load_airports():
    start_time = datetime.utcnow()
    storage_client = get_storage_client()
    # convert latitude and longitude in float 
    csv_text = storage_client.read_text("processed", "airports_processed.csv")
    reader = csv.DictReader(StringIO(csv_text))
    airports = []
    for row in reader:
        row['latitude'] = float(row['latitude'])
        row['longitude'] = float(row['longitude'])
        airports.append(row)
    processed, inserted = _upsert_one_by_one_with_retry(db.airports, airports)
    end_time = datetime.utcnow()
    print(f"Processed {processed} airports (new inserts: {inserted})")
    print(f"Loaded airports in {end_time - start_time}")
    run_with_cosmos_retry(lambda: db.audit_runs.insert_one({
        "process_name": "load_airports",
        "status": "SUCCESS",
        "started_at": start_time,
        "finished_at": end_time,
        "records_processed": processed,
        "records_inserted": inserted,
        "errors": []
    }))

if __name__ == "__main__":
    load_airports()
