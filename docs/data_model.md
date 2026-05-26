# NoSQL Data Model

AeroOps NoSQL Control Tower uses a document-oriented data model designed for operational aviation/travel workloads.

The goal is not to normalize data like in a relational database. The goal is to organize documents around the most important operational access patterns, such as flight lookup, delay monitoring, event timelines, impacted passenger discovery, and audit review.

## Collections

The system uses five MongoDB collections:

1. `flights`
2. `flight_events`
3. `passenger_itineraries`
4. `airports`
5. `audit_runs`

---

## 1. flights

The `flights` collection stores the main operational flight records.

Each document represents one flight occurrence on a specific date.

### Example document

```json
{
  "flight_id": "2024-01-15-AA-1205-JFK-LAX",
  "flight_date": "2024-01-15",
  "airline": "AA",
  "flight_number": "1205",
  "origin": "JFK",
  "destination": "LAX",
  "scheduled_departure": "2024-01-15T08:30:00",
  "actual_departure": "2024-01-15T09:10:00",
  "departure_delay_minutes": 40,
  "arrival_delay_minutes": 25,
  "status": "DELAYED",
  "cancelled": false,
  "diverted": false,
  "distance": 2475,
  "tail_number": "N123AA",
  "created_at": "2026-05-25T20:00:00"
}
```

### Why this is document-oriented

A flight is naturally represented as a document because most operational queries need the flight details together: route, date, airline, delay, status, and aircraft metadata.

---

## 2. flight_events

The `flight_events` collection stores operational events related to a flight.

A flight can have many events over time.

### Example document

```json
{
  "event_id": "evt_001",
  "flight_id": "2024-01-15-AA-1205-JFK-LAX",
  "event_type": "DELAY_REPORTED",
  "timestamp": "2024-01-15T08:45:00",
  "message": "Departure delay increased to 40 minutes.",
  "source": "synthetic_event_generator"
}
```

### Why events are separate

Events are stored separately from the flight document because event timelines can grow over time. Keeping them in a separate collection avoids unbounded document growth.

---

## 3. passenger_itineraries

The `passenger_itineraries` collection stores synthetic passenger itineraries.

No real personal data is used.

### Example document

```json
{
  "passenger_id": "pax_0001",
  "synthetic_name": "Synthetic Passenger 0001",
  "itinerary_id": "itin_0001",
  "flights": [
    "2024-01-15-AA-1205-JFK-LAX",
    "2024-01-15-AA-3310-LAX-SFO"
  ],
  "connection_risk": true,
  "risk_reason": "First flight delayed more than 30 minutes",
  "created_at": "2026-05-25T20:00:00"
}
```

### Why flights are embedded as an array

The array of flight IDs allows the API to quickly find passengers impacted by a specific flight.

---

## 4. airports

The `airports` collection stores airport metadata from OurAirports.

### Example document

```json
{
  "iata_code": "JFK",
  "icao_code": "KJFK",
  "name": "John F Kennedy International Airport",
  "municipality": "New York",
  "country": "United States",
  "latitude": 40.639801,
  "longitude": -73.7789,
  "airport_type": "large_airport"
}
```

### Why airports are separate

Airport metadata is reused by many flights. Keeping it separate avoids duplicating full airport details in every flight document.

---

## 5. audit_runs

The `audit_runs` collection stores process execution history.

It tracks ingestion, data processing, index creation, synthetic event generation, and validation checks.

### Example document

```json
{
  "run_id": "run_20260525_001",
  "process_name": "load_flights",
  "status": "SUCCESS",
  "started_at": "2026-05-25T22:30:00",
  "finished_at": "2026-05-25T22:31:15",
  "records_processed": 10000,
  "records_inserted": 10000,
  "errors": []
}
```

### Why audit runs matter

Audit runs make the system easier to debug, explain, and trust. They show what process ran, when it ran, how many records it handled, and whether it succeeded.

