from datetime import datetime
import random
from app.database import db


def generate_passengers():
    started_at = datetime.utcnow()

    db.passenger_itineraries.delete_many({})

    impacted_flights = list(
        db.flights.find(
            {"status": {"$in": ["DELAYED", "CANCELLED"]}},
            {"flight_id": 1, "status": 1, "origin": 1, "destination": 1, "_id": 0},
        ).limit(300)
    )
    all_flights = list(
        db.flights.find(
            {},
            {"flight_id": 1, "origin": 1, "destination": 1, "_id": 0},
        ).limit(5000)
    )

    passenger_docs = []
    random.seed(42)

    for index, flight in enumerate(impacted_flights, start=1):
        flight_id = flight["flight_id"]
        status = flight["status"]
        legs = random.choice([1, 2, 2, 3])
        itinerary_flights = [flight_id]

        # Build multi-leg itineraries by appending additional flights that do not
        # duplicate the impacted leg. This keeps the dataset synthetic but
        # produces more realistic connection patterns for analytics.
        if legs > 1 and all_flights:
            extra_pool = [f for f in all_flights if f["flight_id"] != flight_id]
            random.shuffle(extra_pool)
            for candidate in extra_pool[: legs - 1]:
                itinerary_flights.append(candidate["flight_id"])

        impacted_leg_idx = 0
        if len(itinerary_flights) > 1:
            impacted_leg_idx = random.choice(range(len(itinerary_flights)))
            itinerary_flights[0], itinerary_flights[impacted_leg_idx] = (
                itinerary_flights[impacted_leg_idx],
                itinerary_flights[0],
            )

        is_connection_risk = impacted_leg_idx < len(itinerary_flights) - 1

        passenger_docs.append({
            "passenger_id": f"pax_{index:06d}",
            "synthetic_name": f"Synthetic Passenger {index:06d}",
            "itinerary_id": f"itin_{index:06d}",
            "flights": itinerary_flights,
            "connection_risk": is_connection_risk,
            "risk_reason": (
                f"Itinerary includes a {status.lower()} flight on leg "
                f"{impacted_leg_idx + 1} of {len(itinerary_flights)}."
            ),
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
