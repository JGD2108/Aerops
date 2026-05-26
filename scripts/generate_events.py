from datetime import datetime, timedelta

from app.database import db


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

    db.flight_events.delete_many({})

    flights = list(db.flights.find({}).limit(500))

    events = []
    event_counter = 1

    for flight in flights:
        flight_id = flight["flight_id"]
        status = flight.get("status", "SCHEDULED")
        delay = flight.get("departure_delay_minutes", 0)
        flight_date = flight.get("flight_date")
        scheduled_departure = flight.get("scheduled_departure", "0000")

        # Every flight gets a STATUS_CHANGED event
        events.append({
            "event_id": f"evt_{event_counter:06d}",
            "flight_id": flight_id,
            "event_type": "STATUS_CHANGED",
            "timestamp": build_timestamp(flight_date, scheduled_departure, -30),
            "message": f"Flight {flight_id} status set to {status}.",
            "source": EVENT_SOURCE,
        })
        event_counter += 1

        if status == "DELAYED":
            events.append({
                "event_id": f"evt_{event_counter:06d}",
                "flight_id": flight_id,
                "event_type": "DELAY_REPORTED",
                "timestamp": build_timestamp(flight_date, scheduled_departure, -15),
                "message": f"Departure delay of {delay} minutes reported for flight {flight_id}.",
                "source": EVENT_SOURCE,
            })
            event_counter += 1

        if status == "CANCELLED":
            events.append({
                "event_id": f"evt_{event_counter:06d}",
                "flight_id": flight_id,
                "event_type": "CANCELLED",
                "timestamp": build_timestamp(flight_date, scheduled_departure, -60),
                "message": f"Flight {flight_id} was cancelled.",
                "source": EVENT_SOURCE,
            })
            event_counter += 1

        if status == "DEPARTED":
            events.append({
                "event_id": f"evt_{event_counter:06d}",
                "flight_id": flight_id,
                "event_type": "DEPARTED",
                "timestamp": build_timestamp(flight_date, scheduled_departure, int(delay)),
                "message": f"Flight {flight_id} departed.",
                "source": EVENT_SOURCE,
            })
            event_counter += 1

    if events:
        db.flight_events.insert_many(events)

    finished_at = datetime.utcnow()

    db.audit_runs.insert_one({
        "process_name": "generate_events",
        "status": "SUCCESS",
        "started_at": started_at,
        "finished_at": finished_at,
        "records_processed": len(flights),
        "records_inserted": len(events),
        "errors": []
    })

    print(f"Processed {len(flights)} flights")
    print(f"Inserted {len(events)} flight events")
    print(f"Generated events in {finished_at - started_at}")


if __name__ == "__main__":
    generate_events()