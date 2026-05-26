# AeroOps Cloud-Native Deployment (Azure Container Apps)

## Production Target

- `aeroops-api` as Azure Container App (public ingress, `/health` and `/ready` probes).
- `aeroops-dashboard` as Azure Container App (public ingress, API-backed).
- `aeroops-pipeline-job` as Azure Container Apps Job (manual + scheduled runs).
- `Cosmos DB for MongoDB` for operational collections and analytics snapshots.
- `Azure Blob Storage` for `raw/` and `processed/` datasets.
- `Log Analytics` + `Application Insights` for centralized observability.

## Runtime Configuration Contract

Required:

- `MONGODB_URI`
- `MONGODB_DATABASE` (or legacy `MONGODB_DB_NAME`)
- `STORAGE_BACKEND=azure_blob`
- `AZURE_STORAGE_CONNECTION_STRING`
- `RAW_CONTAINER`
- `PROCESSED_CONTAINER`

Optional:

- `AZURE_PIPELINE_TRIGGER_URL`
- `AZURE_PIPELINE_TRIGGER_TOKEN`
- `RAW_PREFIX`
- `PROCESSED_PREFIX`

For production, store secrets in Key Vault-backed secret references (or ACA secrets as interim).

## Pipeline Contract

- Entry point: `python -m scripts.run_pipeline`
- Behavior: incremental-first (no full collection wipes in load/generation steps).
- Idempotency:
  - `flights.flight_id` unique
  - `ops_metrics_snapshots.snapshot_id` unique
- Cosmos throttling handling:
  - retries on 429 / 16500 for write, delete, update, index, and audit operations.
- Exit behavior:
  - returns non-zero only on non-recoverable failures.

## Container App Commands

- API:
  - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Dashboard:
  - `streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0`
- Pipeline Job:
  - `python -m scripts.run_pipeline`

## Scheduling and Concurrency

- Schedule cron: daily off-peak UTC (example `0 3 * * *`).
- Concurrency policy: single active execution for pipeline job.
- Keep manual trigger enabled for operations/debugging.

## Operational Validation

- API responds successfully on `/health` and `/ready`.
- Dashboard loads and consumes API metrics.
- Manual job execution ends in `SUCCESS`.
- Scheduled job runs successfully in next windows.
- Logs show retried throttling instead of unhandled failures.
