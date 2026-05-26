import csv 
from datetime import datetime

from app.database import db

CSV_FILE = "./data/processed/airports_processed.csv"

def load_airports():
    start_time = datetime.utcnow()
    db.airports.delete_many({})
    # convert latitude and longitude in float 
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        airports = []
        for row in reader:
            row['latitude'] = float(row['latitude'])
            row['longitude'] = float(row['longitude'])
            airports.append(row)
        db.airports.insert_many(airports)
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
