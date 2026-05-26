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