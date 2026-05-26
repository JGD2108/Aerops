from app.database import db


def serialize_document(document):
    if not document:
        return None

    document["_id"] = str(document["_id"])
    return document


def get_flight_by_id(flight_id: str):
    document = db.flights.find_one({"flight_id": flight_id})
    return serialize_document(document)


def get_flights_by_status(status: str, limit: int = 50):
    cursor = (
        db.flights
        .find({"status": status.upper()})
        .sort("flight_date", -1)
        .limit(limit)
    )

    return [serialize_document(document) for document in cursor]


def get_flights_by_origin(origin: str, limit: int = 50):
    cursor = (
        db.flights
        .find({"origin": origin.upper()})
        .sort("flight_date", -1)
        .limit(limit)
    )

    return [serialize_document(document) for document in cursor]

def get_events_by_flight_id(flight_id: str, limit: int = 50):
    cursor = (
        db.flight_events
        .find({"flight_id": flight_id})
        .sort("timestamp", -1)
        .limit(limit)
    )

    events = []

    for document in cursor:
        document["_id"] = str(document["_id"])

        if "timestamp" in document:
            document["timestamp"] = document["timestamp"].isoformat()

        events.append(document)

    return events

def get_impacted_passengers_by_flight_id(flight_id: str, limit: int = 50):
    cursor = (
        db.passenger_itineraries
        .find({"flights": flight_id})
        .limit(limit)
    )

    passengers = []

    for document in cursor:
        document["_id"] = str(document["_id"])

        if "created_at" in document:
            document["created_at"] = document["created_at"].isoformat()

        passengers.append(document)

    return passengers