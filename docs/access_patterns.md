# Access Patterns

AeroOps NoSQL Control Tower is designed around operational aviation/travel access patterns.

In NoSQL systems, the data model should be shaped by the queries the application needs to serve efficiently.

---

## Core Access Patterns

### 1. Look up one flight by flight_id

Endpoint:

```http
GET /flights/{flight_id}
```

Purpose:

Retrieve the full operational record for a specific flight.

Supporting index:

```javascript
{ flight_id: 1 }
```

### 2. Query flights by origin airport

Endpoint:

```http
GET /flights/origin/{origin}
```

Purpose:

Find flights departing from a specific airport.

Supporting index:

```javascript
{ origin: 1, flight_date: 1 }
```

### 3. Query flights by status

Endpoint:

```http
GET /flights/status/{status}
```

Purpose:

Find flights by operational status, such as DELAYED, CANCELLED, DEPARTED, or ARRIVED.

Supporting index:

```javascript
{ status: 1, flight_date: 1 }
```

### 4. Retrieve event timeline for a flight

Endpoint:

```http
GET /flights/{flight_id}/events
```

Purpose:

Show the operational sequence of events for one flight.

Supporting index:

```javascript
{ flight_id: 1, timestamp: -1 }
```

### 5. Find passengers impacted by a flight

Endpoint:

```http
GET /flights/{flight_id}/impacted-passengers
```

Purpose:

Find synthetic passenger itineraries that include a delayed or cancelled flight.

Supporting index:

```javascript
{ flights: 1 }
```

### 6. Get delay summary

Endpoint:

```http
GET /ops/delay-summary
```

Purpose:

Summarize operational delay metrics across the loaded flight data.

Possible metrics:

- Total flights
- Delayed flights
- Cancelled flights
- Average departure delay
- Average arrival delay

Supporting indexes:

```javascript
{ status: 1, flight_date: 1 }
{ departure_delay_minutes: -1 }
```

### 7. Review audit runs

Endpoint:

```http
GET /audit/runs
```

Purpose:

Review ingestion, data processing, indexing, and synthetic data generation history.

Supporting index:

```javascript
{ started_at: -1 }
```