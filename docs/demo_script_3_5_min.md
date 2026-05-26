# AeroOps Demo Script (3-5 minutes)

## 0) Setup

```powershell
docker compose up -d --build
docker compose exec api python -m scripts.build_analytics_snapshots
```

## 1) Architecture framing (30-45s)

Open `README.md` and explain:

- Operational layer: MongoDB + FastAPI access patterns
- Analytics layer: aggregation + batch snapshots
- Presentation layer: Streamlit Live/Snapshot dashboard

## 2) Runtime proof (20-30s)

```powershell
docker compose ps
```

Show `mongo`, `api`, and `dashboard` are `Up`.

## 3) API proof (60-90s)

Open Swagger: `http://localhost:8000/docs`

Call:

1. `GET /health`
2. `GET /ready`
3. `GET /ops/delay-summary`
4. `GET /ops/metrics-snapshots/latest`

Point out the `snapshot_id` and precomputed metrics.

## 4) Dashboard proof (90-120s)

Open dashboard: `http://localhost:8501`

Show:

1. KPIs and Ops Summary
2. Route Analysis or Airport Analysis
3. Switch `Data mode` from `Live` to `Snapshot`
4. Snapshot history in Audit tab

## 5) Infra readiness (30-45s)

Show:

- `infra/k8s/` manifests
- (Optional) `kubectl get all -n aeroops`
- ACR screenshot with `aeroops-api:latest`

## 6) Closing message (15-20s)

Use this line:

`The dashboard is the final consumer of a NoSQL operational data platform with ingestion, indexing, API access patterns, auditability, batch analytics snapshots, Docker, Kubernetes, and Azure-ready deployment.`
