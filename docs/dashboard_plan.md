# Dashboard Plan (Phase 12)

## Objective
Define a minimal analytics scope that extends the current operational API without changing the project focus.

## Architecture Decision
The dashboard must consume FastAPI endpoints only:

`Dashboard -> FastAPI -> MongoDB`

No direct dashboard connection to MongoDB.

## Dashboard v1 Views
1. Executive Ops Summary
2. Route Delay Performance
3. Cancellations by Airport
4. Passenger Impact + Audit Runs

## Existing Endpoints Reused
- `GET /ops/delay-summary`
- `GET /audit/runs`
- `GET /flights/{flight_id}/impacted-passengers`

## New Analytics Endpoints (v1)
### 1) `GET /ops/top-delayed-routes`
Purpose: rank operationally problematic routes.

Suggested query params:
- `limit` (default 10)
- `min_flights` (default 5)

Response fields per route:
- `origin`
- `destination`
- `total_flights`
- `delayed_flights`
- `avg_departure_delay`
- `max_departure_delay`
- `delay_rate_pct`

### 2) `GET /ops/cancellations-by-airport`
Purpose: identify origin airports with the highest cancellation pressure.

Suggested query params:
- `limit` (default 20)
- `min_flights` (default 10)

Response fields per airport:
- `origin`
- `total_flights`
- `cancelled_flights`
- `cancellation_rate_pct`

### 3) `GET /ops/passenger-impact-summary`
Purpose: summarize business/customer impact from operational disruption.

Response fields:
- `total_itineraries`
- `impacted_itineraries`
- `impact_rate_pct`
- `connection_risk_count`
- `top_impacted_flights` (array of `{ flight_id, impacted_itineraries }`)

## Non-Goals for v1
- No Kafka/Spark/Airflow
- No real-time streaming
- No auth/user management
- No React dashboard in this phase

## Implementation Order After Phase 12
1. Add v1 analytics endpoints in FastAPI
2. Build Streamlit dashboard consuming those endpoints
3. Add analytics snapshot batch (`ops_metrics_snapshots`)
4. Add dashboard service to Docker Compose

