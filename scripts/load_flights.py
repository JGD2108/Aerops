
import csv 
from datetime import datetime
from io import StringIO

from app.database import db
from app.storage_client import get_storage_client
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
        db.flights.insert_many(flights)
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
