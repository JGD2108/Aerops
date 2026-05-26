# Cloud Pipeline Automation

This document defines the cloud-native automation path for AeroOps pipeline execution.

## Goal

Automate ingestion and transformation jobs without running long processes inside the FastAPI web service.

## Current Orchestration (MVP)

The project now has a single orchestration entrypoint:

```powershell
python -m scripts.run_pipeline
```

`run_pipeline` executes these steps in order:

1. `process_raw_data`
2. `load_airports`
3. `load_flights`
4. `create_indexes`
5. `generate_events`
6. `generate_passengers`
7. `build_analytics_snapshots`

The pipeline writes a consolidated `audit_runs` record with:

- `process_name = run_pipeline`
- step-level status and duration
- overall pipeline status (`SUCCESS` / `FAILED`)

## Recommended Azure Automation Architecture

```text
BTS / OurAirports source files
        ↓
Azure Blob Storage (raw / processed)
        ↓
Azure Container Apps Job (scheduled or manual)
        ↓
python -m scripts.run_pipeline
        ↓
Cosmos DB for MongoDB collections + audit_runs + ops_metrics_snapshots
        ↓
FastAPI + Streamlit dashboard (Live / Snapshot)
```

## Why the API Should Not Run the Pipeline Internally

- Batch execution can be long-running and resource-intensive.
- Running inside API workers can block web traffic.
- Operational retries and scheduling are cleaner at job level.

Recommended pattern:

```text
POST /pipeline/run (trigger only)
        ↓
Azure job execution
        ↓
audit_runs + snapshots
```

Current API support:

- `POST /pipeline/run`
- Requires `AZURE_PIPELINE_TRIGGER_URL`
- Optional `AZURE_PIPELINE_TRIGGER_TOKEN` (Bearer)

## Azure Components

- `Azure Blob Storage`: source and processed files.
- `Azure Container Apps Jobs`: scheduled/manual batch execution.
- `Azure Cosmos DB for MongoDB`: operational and analytics collections.
- `Azure Container Registry`: image hosting and promotion.

## Next Increment

1. `storage_client` abstraction is now implemented (`local` / `azure_blob`) and used by ingestion scripts.
2. `POST /pipeline/run` trigger endpoint is now implemented (job dispatch only).
3. Add scheduling configuration docs for Container Apps Jobs.

## Storage Abstraction Variables

```text
STORAGE_BACKEND=local|azure_blob
AZURE_STORAGE_CONNECTION_STRING=...
RAW_CONTAINER=aeroops-raw
PROCESSED_CONTAINER=aeroops-processed
RAW_PREFIX=
PROCESSED_PREFIX=
```

Current ingestion scripts using storage abstraction:

- `scripts/process_raw_data.py`
- `scripts/load_airports.py`
- `scripts/load_flights.py`
