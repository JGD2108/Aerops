# Cloud Pipeline Automation

This document defines the cloud-native automation path for AeroOps pipeline execution.

## Goal

Automate ingestion and transformation jobs without running long processes inside the FastAPI web service.

## Current Orchestration

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

The pipeline is incremental-first and writes a consolidated `audit_runs` record with:

- `process_name = run_pipeline`
- step-level status and duration
- overall pipeline status (`SUCCESS` / `FAILED`)
- Cosmos throttling retries on write/delete/update/index paths

## Recommended Azure Automation Architecture (Prod)

```text
BTS / OurAirports source files
        ↓
Azure Blob Storage (raw / processed)
        ↓
Azure Container Apps Job (scheduled/manual, single active execution)
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
- `Azure Container Apps`: API and dashboard runtime.
- `Azure Cosmos DB for MongoDB`: operational and analytics collections.
- `Azure Container Registry`: image hosting and promotion.
- `Log Analytics + Application Insights`: logs, traces, alerts.

## Deployment Contract

See:

```text
docs/cloud_native_deployment_aca.md
```

## Phase 19 Execution (Completed)

The Azure scheduler baseline has been provisioned in subscription `aaa155cc-3eca-463e-ac45-20ab5528d131`:

- Allowed regions discovered from policy `sys.regionrestriction`:
  - `southcentralus`, `canadacentral`, `eastus2`, `mexicocentral`, `westus2`
- Container Apps Environment:
  - `aeroops-ca-env` in `eastus2`
- ACR image used:
  - `aeroopsacr1974.azurecr.io/aeroops-api:latest`
- Jobs created:
  - Manual: `aeroops-pipeline-job`
  - Scheduled: `aeroops-pipeline-job-sched` with cron `0 3 * * *` (UTC)

Validation commands:

```powershell
az containerapp job list --resource-group rg-aeroops-nosql --query "[].{name:name,trigger:properties.configuration.triggerType,cron:properties.configuration.scheduleTriggerConfig.cronExpression}" -o table
az containerapp job start --name aeroops-pipeline-job --resource-group rg-aeroops-nosql
az containerapp job execution list --name aeroops-pipeline-job --resource-group rg-aeroops-nosql
```

Current constraint:

- The Azure job execution path still needs a cloud-reachable MongoDB endpoint (`Cosmos DB for MongoDB` or `MongoDB Atlas`).
- A local URI such as `mongodb://localhost:27017` is not reachable from Container Apps.

Until MongoDB is cloud-reachable, Azure executions can start but cannot complete end-to-end pipeline writes.

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
