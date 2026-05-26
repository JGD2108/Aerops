from datetime import datetime, timedelta

from app.database import db
from scripts.cosmos_retry import run_with_cosmos_retry


EVENT_SOURCE = "derived_from_bts_flight_record"


def build_timestamp(flight_date: str, scheduled_departure: str, offset_minutes: int = 0):
    try:
        hour = int(scheduled_departure[:2])
        minute = int(scheduled_departure[2:])
        base = datetime.strptime(flight_date, "%Y-%m-%d")
        return base.replace(hour=hour, minute=minute) + timedelta(minutes=offset_minutes)
    except Exception:
        return datetime.utcnow()


def generate_events():
    started_at = datetime.utcnow()
    flights = list(db.flights.find({}).limit(500))

    events = []

    for flight in flights:
        flight_id = flight["flight_id"]
        status = flight.get("status", "SCHEDULED")
        delay = flight.get("departure_delay_minutes", 0)
        flight_date = flight.get("flight_date")
        scheduled_departure = flight.get("scheduled_departure", "0000")

        flight_events = [{
            "event_id": f"evt_{flight_id}_STATUS_CHANGED",
            "flight_id": flight_id,
            "event_type": "STATUS_CHANGED",
            "timestamp": build_timestamp(flight_date, scheduled_departure, -30),
            "message": f"Flight {flight_id} status set to {status}.",
            "source": EVENT_SOURCE,
        }]

        if status == "DELAYED":
            flight_events.append({
                "event_id": f"evt_{flight_id}_DELAY_REPORTED",
                "flight_id": flight_id,
                "event_type": "DELAY_REPORTED",
                "timestamp": build_timestamp(flight_date, scheduled_departure, -15),
                "message": f"Departure delay of {delay} minutes reported for flight {flight_id}.",
                "source": EVENT_SOURCE,
            })

        if status == "CANCELLED":
            flight_events.append({
                "event_id": f"evt_{flight_id}_CANCELLED",
                "flight_id": flight_id,
                "event_type": "CANCELLED",
                "timestamp": build_timestamp(flight_date, scheduled_departure, -60),
                "message": f"Flight {flight_id} was cancelled.",
                "source": EVENT_SOURCE,
            })

        if status == "DEPARTED":
            flight_events.append({
                "event_id": f"evt_{flight_id}_DEPARTED",
                "flight_id": flight_id,
                "event_type": "DEPARTED",
                "timestamp": build_timestamp(flight_date, scheduled_departure, int(delay)),
                "message": f"Flight {flight_id} departed.",
                "source": EVENT_SOURCE,
            })

        current_types = [event["event_type"] for event in flight_events]
        run_with_cosmos_retry(
            lambda: db.flight_events.delete_many(
                {"flight_id": flight_id, "source": EVENT_SOURCE, "event_type": {"$nin": current_types}}
            )
        )
        for event in flight_events:
            run_with_cosmos_retry(
                lambda event_doc=event: db.flight_events.replace_one(
                    {"event_id": event_doc["event_id"]},
                    event_doc,
                    upsert=True,
                )
            )
        events.extend(flight_events)

    finished_at = datetime.utcnow()

    run_with_cosmos_retry(lambda: db.audit_runs.insert_one({
        "process_name": "generate_events",
        "status": "SUCCESS",
        "started_at": started_at,
        "finished_at": finished_at,
        "records_processed": len(flights),
        "records_inserted": len(events),
        "errors": []
    }))

    print(f"Processed {len(flights)} flights")
    print(f"Inserted {len(events)} flight events")
    print(f"Generated events in {finished_at - started_at}")


if __name__ == "__main__":
    generate_events()
