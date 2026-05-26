
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
            lambda: collection.replace_one({"flight_id": doc["flight_id"]}, doc, upsert=True)
        )
        if result.upserted_id is not None:
            inserted += 1
    return processed, inserted


def to_bool(value):
    return str(value).lower() == "true"
def load_flights():
    start_time = datetime.utcnow()
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
        row['departure_delay_minutes'] = float(row.get('departure_delay_minutes') or 0)
        row['arrival_delay_minutes'] = float(row.get('arrival_delay_minutes') or 0)
        row['distance'] = float(row.get('distance') or 0)
        row['cancelled'] = to_bool(row['cancelled'])
        row['diverted'] = to_bool(row['diverted'])
        
        flights.append(row)
    if flights:
        processed, inserted = _upsert_one_by_one_with_retry(db.flights, flights)
    else:
        processed = 0
        inserted = 0
    end_time = datetime.utcnow()
    print(f"Processed {processed} flights (new inserts: {inserted})")
    print(f"Loaded flights in {end_time - start_time}")
    run_with_cosmos_retry(lambda: db.audit_runs.insert_one({
        "process_name": "load_flights",
        "status": "SUCCESS",
        "started_at": start_time,
        "finished_at": end_time,
        "records_processed": processed,
        "records_inserted": inserted,
        "errors": []
    }))
    
if __name__ == "__main__":
    load_flights()
