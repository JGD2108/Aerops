# AeroOps NoSQL Control Tower

AeroOps NoSQL Control Tower is a cloud-native operational data platform for aviation/travel workloads.

It models flights, operational flight events, airports, audit runs, and synthetic passenger itineraries using MongoDB-style NoSQL design. The API supports low-latency operational access patterns such as delayed flight lookup, event timelines, impacted passenger queries, delay summaries, and audit run review.

## Business Context

This project was built to align with a Data Engineer - Operational Data (NoSQL) opportunity in the aviation/travel technology sector.

The role emphasizes distributed operational data systems, NoSQL databases, data model design, backend development, indexing strategies, cloud-native architecture, Kubernetes, and Azure.

## Why This Project Matches the Role

This project demonstrates:

- NoSQL document modeling with MongoDB.
- Operational access patterns for aviation/travel workloads.
- Python backend development with FastAPI.
- Data ingestion and transformation from external aviation datasets.
- MongoDB indexing strategy.
- Auditability through `audit_runs`.
- Dockerized local execution.
- Kubernetes deployment with liveness and readiness probes.
- Azure-ready architecture using Azure Container Registry, AKS, and Cosmos DB for MongoDB.

## Architecture

The platform is organized in two layers:

* Operational layer: FastAPI + MongoDB + Kubernetes-ready API patterns.
* Analytics layer: aggregation endpoints + Streamlit operational dashboard.

```text
BTS / OurAirports CSV datasets
	↓
Python processing scripts
	↓
Processed operational records
	↓
MongoDB collections
	↓
FastAPI operational API
	↓
Analytics aggregation endpoints
	↓
Streamlit operational dashboard
	↓
Docker image
	↓
Docker Compose / Kubernetes
	↓
Azure-ready path: ACR + AKS + Cosmos DB for MongoDB
```

## Data Sources

### BTS Airline On-Time Performance Data

Used for real historical flight records, including:

* Flight date
* Airline
* Flight number
* Origin
* Destination
* Scheduled departure
* Actual departure
* Departure delay
* Arrival delay
* Cancellation status
* Distance
* Tail number

### OurAirports CSV Data

Used for airport metadata, including:

* IATA code
* ICAO code
* Airport name
* Municipality
* Country
* Latitude
* Longitude
* Airport type

### Synthetic Passenger Data

Passenger itineraries are synthetic demo records. They do not represent real passengers or personal data.

They are generated only to demonstrate the impacted-passenger access pattern for delayed and cancelled flights.

## NoSQL Data Model

The project uses five MongoDB collections:

| Collection              | Purpose                                           |
| ----------------------- | ------------------------------------------------- |
| `flights`               | Main operational flight records                   |
| `flight_events`         | Derived event timelines from BTS flight records   |
| `passenger_itineraries` | Synthetic passenger itineraries for impact lookup |
| `airports`              | Airport metadata from OurAirports                 |
| `audit_runs`            | Ingestion, indexing, and generation audit history |

## Flight Events

Flight events are derived from BTS flight records.

Events such as `STATUS_CHANGED`, `DELAY_REPORTED`, `CANCELLED`, and `DEPARTED` are generated from real flight-level fields such as status, departure delay, cancellation flag, scheduled departure, and actual departure.

The current MVP does not generate random operational events such as gate changes.

## Access Patterns

The API supports the following operational access patterns:

| Access Pattern           | Endpoint                                       | Supporting Index                  |
| ----------------------- | ---------------------------------------------- | --------------------------------- |
| Look up one flight       | `GET /flights/{flight_id}`                     | `{ flight_id: 1 }` unique         |
| Query flights by status  | `GET /flights/status/{status}`                 | `{ status: 1, flight_date: 1 }`   |
| Query flights by origin  | `GET /flights/origin/{origin}`                 | `{ origin: 1, flight_date: 1 }`   |
| Retrieve event timeline  | `GET /flights/{flight_id}/events`              | `{ flight_id: 1, timestamp: -1 }` |
| Find impacted passengers | `GET /flights/{flight_id}/impacted-passengers` | `{ flights: 1 }`                  |
| Delay summary            | `GET /ops/delay-summary`                       | `{ departure_delay_minutes: -1 }` |
| Audit run review         | `GET /audit/runs`                              | `{ started_at: -1 }`              |

## Indexing Strategy

The project creates these MongoDB indexes:

### `flights`

```javascript
{ flight_id: 1 } unique
{ origin: 1, flight_date: 1 }
{ destination: 1, flight_date: 1 }
{ status: 1, flight_date: 1 }
{ departure_delay_minutes: -1 }
```

### `flight_events`

```javascript
{ flight_id: 1, timestamp: -1 }
```

### `passenger_itineraries`

```javascript
{ flights: 1 }
```

### `audit_runs`

```javascript
{ started_at: -1 }
```

Indexes were designed around API access patterns instead of indexing every field.

## Sharding Strategy

Real sharding is not implemented in the MVP.

For a larger distributed MongoDB or Cosmos DB for MongoDB deployment, the suggested shard key is:

```javascript
{ flight_date: 1, origin: 1 }
```

This supports common aviation/travel operational queries by date and airport while helping distribute daily flight workloads across partitions.

Alternative shard key candidates:

```javascript
{ airline: 1, flight_date: 1 }
{ origin: 1, scheduled_departure: 1 }
```

## API Endpoints

### Health

```http
GET /health
GET /ready
```

### Flights

```http
GET /flights/{flight_id}
GET /flights/status/{status}
GET /flights/origin/{origin}
GET /flights/{flight_id}/events
GET /flights/{flight_id}/impacted-passengers
```

### Operations

```http
GET /ops/delay-summary
GET /ops/top-delayed-routes
GET /ops/cancellations-by-airport
GET /ops/passenger-impact-summary
GET /ops/metrics-snapshots/latest
GET /ops/metrics-snapshots
```

### Audit

```http
GET /audit/runs
```

## Dashboard

The project includes a Streamlit Operational Control Tower dashboard under:

```text
dashboard/
```

Dashboard views:

* Ops Summary: executive KPIs, delay rate, cancellation rate, and disruption posture.
* Route Analysis: ranked delayed routes with configurable minimum-flight thresholds.
* Airport Analysis: cancellation pressure by origin airport.
* Passenger Impact: impacted itineraries, connection-risk count, and top impacted flights.
* Audit Runs: recent ingestion, indexing, and generation jobs.

Dashboard URL:

```text
http://localhost:8501
```

## Local Setup with Docker Compose

Build and run MongoDB, API, and dashboard:

```powershell
docker compose up --build
```

Open Swagger:

```text
http://localhost:8000/docs
```

Open dashboard:

```text
http://localhost:8501
```

Health checks:

```text
http://localhost:8000/health
http://localhost:8000/ready
```

## Analytics Dashboard Demo Flow

Recommended demo sequence:

1. Open Swagger at `http://localhost:8000/docs` and show the `/ops` endpoint group.
2. Open the dashboard at `http://localhost:8501`.
3. Start with Ops Summary to explain total flights, delay rate, cancellation rate, and average delay.
4. Move to Route Analysis and adjust the route minimum-flight threshold in the sidebar.
5. Move to Airport Analysis and compare cancellation pressure by origin airport.
6. Move to Passenger Impact and show impacted itineraries plus `connection_risk_count`.
7. Finish with Audit Runs to show pipeline traceability.

This flow demonstrates the full operational analytics path:

```text
MongoDB operational collections
	↓
FastAPI aggregation endpoints
	↓
Streamlit analytics dashboard
	↓
Operational monitoring story
```

## Data Processing and Loading

Process raw datasets:

```powershell
python scripts/process_raw_data.py
```

Load MongoDB collections:

```powershell
python -m scripts.load_airports
python -m scripts.load_flights
python -m scripts.create_indexes
```

Generate derived flight events and synthetic passenger itineraries:

```powershell
python -m scripts.generate_events
python -m scripts.generate_passengers
```

Build analytics snapshots:

```powershell
python -m scripts.build_analytics_snapshots
```

## Kubernetes Deployment

The project includes Kubernetes manifests under:

```text
infra/k8s/
```

Resources include:

* Namespace
* ConfigMap
* Secret example
* Deployment
* Service
* Horizontal Pod Autoscaler
* Liveness probe using `/health`
* Readiness probe using `/ready`
* CPU and memory requests/limits
* 2 API replicas

Apply manifests:

```powershell
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.example.yaml
kubectl apply -f infra/k8s/deployment.yaml
kubectl apply -f infra/k8s/service.yaml
kubectl apply -f infra/k8s/hpa.yaml
```

Port-forward:

```powershell
kubectl port-forward svc/aeroops-api-service 8001:80 -n aeroops
```

Open:

```text
http://localhost:8001/docs
```

## Azure Deployment Path

The project is Azure-ready.

Target Azure services:

* Azure Cosmos DB for MongoDB
* Azure Container Registry
* Azure Kubernetes Service

Azure Container Registry was validated successfully:

```text
Repository: aeroops-api
Tag: latest
```

AKS and Cosmos DB are documented as the target deployment path. The local MVP does not depend on Azure resources being fully deployed.

## Demo Queries

### Flight lookup

```text
http://localhost:8000/flights/2025-01-01-AA-164-SFO-JFK
```

### Delayed flights

```text
http://localhost:8000/flights/status/DELAYED?limit=5
```

### Flights by origin

```text
http://localhost:8000/flights/origin/SFO?limit=5
```

### Event timeline

```text
http://localhost:8000/flights/2025-01-01-AA-4-LAX-JFK/events
```

### Impacted passengers

```text
http://localhost:8000/flights/2025-01-01-AA-1784-ORD-CLT/impacted-passengers
```

### Delay summary

```text
http://localhost:8000/ops/delay-summary
```

### Top delayed routes

```text
http://localhost:8000/ops/top-delayed-routes?limit=5&min_flights=10
```

### Cancellations by airport

```text
http://localhost:8000/ops/cancellations-by-airport?limit=5&min_flights=50
```

### Passenger impact summary

```text
http://localhost:8000/ops/passenger-impact-summary
```

### Audit runs

```text
http://localhost:8000/audit/runs?limit=5
```

## Screenshots

Recommended screenshots:

1. Swagger UI showing all endpoint groups.
2. `/ops/delay-summary` response.
3. `/ops/top-delayed-routes` response.
4. `/ops/passenger-impact-summary` response.
5. Streamlit dashboard overview (`localhost:8501`).
6. Streamlit Route Analysis tab.
7. Streamlit Passenger Impact tab.
8. Docker Compose logs.
9. Kubernetes `kubectl get all -n aeroops`.
10. Azure Container Registry repository showing `aeroops-api:latest`.

## Future Improvements

* Automate BTS monthly data acquisition.
* Store raw source files in Azure Blob Storage.
* Deploy Mongo-compatible storage through Azure Cosmos DB for MongoDB.
* Deploy the API to AKS using the ACR image.
* Add CI/CD with GitHub Actions.
* Add analytics snapshot collection (`ops_metrics_snapshots`).
* Add airline-level operational summary.
* Add richer passenger connection-risk simulation using realistic connection windows.
* Add observability with structured logs and metrics.
