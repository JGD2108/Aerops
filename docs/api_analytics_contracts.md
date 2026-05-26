# Analytics API Contracts (Phase 12)

This document defines the v1 contract for new analytics endpoints used by the Operational Control Tower Dashboard.

## General Rules
- Base path: `/ops`
- Content type: `application/json`
- Numeric percentages are returned in `[0, 100]` with 2 decimals.
- Delay metrics are in minutes.
- Empty datasets return valid zero/empty responses (no 500, no null root object).

## 1) GET `/ops/top-delayed-routes`

### Purpose
Return ranked route-level delay performance for operational monitoring.

### Query Params
- `limit` (optional, integer, default `10`, min `1`, max `100`)
- `min_flights` (optional, integer, default `5`, min `1`, max `100000`)

### Response 200
```json
{
  "limit": 10,
  "min_flights": 5,
  "results": [
    {
      "origin": "JFK",
      "destination": "LAX",
      "total_flights": 120,
      "delayed_flights": 46,
      "avg_departure_delay": 18.75,
      "max_departure_delay": 97,
      "delay_rate_pct": 38.33
    }
  ]
}
```

### Ranking Logic
Sort by:
1. `delay_rate_pct` desc
2. `avg_departure_delay` desc
3. `total_flights` desc

### Notes
- Include only routes with `total_flights >= min_flights`.
- A flight counts as delayed when `status == "DELAYED"`.

---

## 2) GET `/ops/cancellations-by-airport`

### Purpose
Return airport-level cancellation pressure by origin airport.

### Query Params
- `limit` (optional, integer, default `20`, min `1`, max `200`)
- `min_flights` (optional, integer, default `10`, min `1`, max `100000`)

### Response 200
```json
{
  "limit": 20,
  "min_flights": 10,
  "results": [
    {
      "origin": "ORD",
      "total_flights": 410,
      "cancelled_flights": 22,
      "cancellation_rate_pct": 5.37
    }
  ]
}
```

### Ranking Logic
Sort by:
1. `cancellation_rate_pct` desc
2. `cancelled_flights` desc
3. `total_flights` desc

### Notes
- Include only airports with `total_flights >= min_flights`.
- A flight counts as cancelled when `status == "CANCELLED"`.

---

## 3) GET `/ops/passenger-impact-summary`

### Purpose
Summarize customer impact caused by disrupted flight operations.

### Query Params
- None (v1).

### Response 200
```json
{
  "total_itineraries": 2800,
  "impacted_itineraries": 530,
  "impact_rate_pct": 18.93,
  "connection_risk_count": 146,
  "top_impacted_flights": [
    {
      "flight_id": "AA1234",
      "impacted_itineraries": 34
    }
  ]
}
```

### Impact Logic (v1)
- `total_itineraries`: count of documents in `passenger_itineraries`.
- `impacted_itineraries`: itineraries where at least one flight is currently disrupted (`DELAYED` or `CANCELLED`).
- `impact_rate_pct`: `impacted_itineraries / total_itineraries * 100`.
- `connection_risk_count`: subset of impacted itineraries with 2+ legs where a delayed/cancelled leg is not the final leg.
- `top_impacted_flights`: top 10 flights by number of impacted itineraries.

### Notes
- If `total_itineraries == 0`, `impact_rate_pct = 0`.
- Return `top_impacted_flights: []` when no impacts are found.

---

## Error Handling
- Validation errors: `422 Unprocessable Entity` (FastAPI default for invalid query params).
- Unexpected server errors: `500 Internal Server Error`.

