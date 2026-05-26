# AeroOps Dashboard (Streamlit)

Operational Control Tower dashboard for analytics endpoints exposed by FastAPI.

## Views
- Ops Summary: operational KPIs, delay rate, cancellation rate, and disruption posture.
- Route Analysis: top delayed routes with configurable volume thresholds.
- Airport Analysis: cancellation pressure by origin airport.
- Passenger Impact: impacted itineraries, connection-risk count, and top impacted flights.
- Audit Runs: recent ingestion, indexing, and generation jobs.

## API Dependency
The dashboard consumes FastAPI endpoints only.

Default API base URL:
- `http://localhost:8000`

Override with:
- `AEROOPS_API_BASE_URL`

## Run locally
```powershell
pip install streamlit requests
streamlit run dashboard/app.py
```

Open:
- `http://localhost:8501`

## Dashboard Modes
- `Live`: reads `/ops/delay-summary`, `/ops/top-delayed-routes`, `/ops/cancellations-by-airport`, and `/ops/passenger-impact-summary`.
- `Snapshot`: reads `/ops/metrics-snapshots/latest` plus `/ops/metrics-snapshots` for history.

Snapshot mode requires at least one materialized snapshot:
```powershell
python -m scripts.build_analytics_snapshots
```

## Docker Compose
```powershell
docker compose up --build
```

Open:
- `http://localhost:8501`

## Demo Flow
1. Open the dashboard and review executive KPIs.
2. Use the sidebar filters to increase route and airport minimum-flight thresholds.
3. Review Route Analysis to identify routes with high delay rates and high average delay.
4. Review Airport Analysis to identify cancellation pressure by origin airport.
5. Review Passenger Impact to connect operational disruption with synthetic itinerary exposure.
6. Review Audit Runs to show pipeline traceability.
