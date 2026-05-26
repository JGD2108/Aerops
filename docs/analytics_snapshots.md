# Analytics Snapshots

AeroOps generates analytics snapshots to store dashboard-ready operational metrics in batch mode.

The snapshot layer separates operational MongoDB collections from repeated dashboard aggregations.

## Source Collections

- `flights`
- `passenger_itineraries`
- `audit_runs`

## Target Collection

- `ops_metrics_snapshots`

## Snapshot Model

Each snapshot is a materialized metrics document produced by a batch job.

Recommended fields:

- `snapshot_id` (unique id, e.g. `snapshot_20260526_001`)
- `created_at` (UTC timestamp)
- `source` (fixed value: `mongodb_operational_collections`)
- `metrics`:
  - `total_flights`
  - `delayed_flights`
  - `cancelled_flights`
  - `delay_rate`
  - `cancellation_rate`
  - `average_departure_delay`
  - `average_arrival_delay`
- `top_delayed_routes` (array)
- `cancellations_by_airport` (array)
- `passenger_impact_summary` (object)

Example:

```json
{
  "snapshot_id": "snapshot_20260526_001",
  "created_at": "2026-05-26T00:00:00Z",
  "source": "mongodb_operational_collections",
  "metrics": {
    "total_flights": 10000,
    "delayed_flights": 1466,
    "cancelled_flights": 22,
    "delay_rate": 14.66,
    "cancellation_rate": 0.22,
    "average_departure_delay": 10.45,
    "average_arrival_delay": 8.12
  },
  "top_delayed_routes": [],
  "cancellations_by_airport": [],
  "passenger_impact_summary": {}
}
```

## Why This Matters

Instead of recalculating every metric each time the dashboard loads, the system can generate batch snapshots and let the dashboard read precomputed metrics.

This improves:

- Dashboard responsiveness for heavier aggregations
- Operational/analytics separation of concerns
- Historical metric tracking across runs
- Reproducibility for reporting and demos

## Relationship with the Dashboard

The dashboard can support two modes:

- Live mode: calls `/ops/*` aggregation endpoints directly.
- Snapshot mode: reads latest document from `ops_metrics_snapshots`.

This allows a clear trade-off:

- Live mode for freshest operational state.
- Snapshot mode for stable, precomputed analytics.
