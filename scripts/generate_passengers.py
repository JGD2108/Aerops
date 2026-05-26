from datetime import datetime
from app.database import db


def generate_passengers():
    started_at = datetime.utcnow()

    db.passenger_itineraries.delete_many({})

    impacted_flights = list(
        db.flights.find(
            {"status": {"$in": ["DELAYED", "CANCELLED"]}},
            {"flight_id": 1, "status": 1, "_id": 0},
        ).limit(300)
    )

    passenger_docs = []

    for index, flight in enumerate(impacted_flights, start=1):
        flight_id = flight["flight_id"]
        status = flight["status"]

        passenger_docs.append({
            "passenger_id": f"pax_{index:06d}",
            "synthetic_name": f"Synthetic Passenger {index:06d}",
            "itinerary_id": f"itin_{index:06d}",
            "flights": [flight_id],
            "connection_risk": True,
            "risk_reason": f"Itinerary includes a {status.lower()} flight.",
            "data_classification": "synthetic_demo_data",
            "created_at": datetime.utcnow(),
        })

    if passenger_docs:
        db.passenger_itineraries.insert_many(passenger_docs)

    finished_at = datetime.utcnow()

    db.audit_runs.insert_one({
        "process_name": "generate_passengers",
        "status": "SUCCESS",
        "started_at": started_at,
        "finished_at": finished_at,
        "records_processed": len(impacted_flights),
        "records_inserted": len(passenger_docs),
        "errors": [],
    })

    print(f"Processed {len(impacted_flights)} impacted flights")
    print(f"Inserted {len(passenger_docs)} synthetic passenger itineraries")
    print(f"Generated passengers in {finished_at - started_at}")


if __name__ == "__main__":
    generate_passengers()