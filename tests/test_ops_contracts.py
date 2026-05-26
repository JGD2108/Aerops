import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestOpsContracts(unittest.TestCase):
    @patch("app.routes.ops.get_top_delayed_routes")
    def test_top_delayed_routes_contract(self, mock_repo):
        mock_repo.return_value = {
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
                    "delay_rate_pct": 38.33,
                }
            ],
        }

        response = client.get("/ops/top-delayed-routes?limit=10&min_flights=5")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("limit", payload)
        self.assertIn("min_flights", payload)
        self.assertIn("results", payload)
        self.assertIsInstance(payload["results"], list)
        self.assertGreaterEqual(len(payload["results"]), 1)

        row = payload["results"][0]
        expected_keys = {
            "origin",
            "destination",
            "total_flights",
            "delayed_flights",
            "avg_departure_delay",
            "max_departure_delay",
            "delay_rate_pct",
        }
        self.assertTrue(expected_keys.issubset(set(row.keys())))

    @patch("app.routes.ops.get_cancellations_by_airport")
    def test_cancellations_by_airport_contract(self, mock_repo):
        mock_repo.return_value = {
            "limit": 20,
            "min_flights": 10,
            "results": [
                {
                    "origin": "ORD",
                    "total_flights": 410,
                    "cancelled_flights": 22,
                    "cancellation_rate_pct": 5.37,
                }
            ],
        }

        response = client.get("/ops/cancellations-by-airport?limit=20&min_flights=10")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertIn("limit", payload)
        self.assertIn("min_flights", payload)
        self.assertIn("results", payload)
        self.assertIsInstance(payload["results"], list)
        self.assertGreaterEqual(len(payload["results"]), 1)

        row = payload["results"][0]
        expected_keys = {
            "origin",
            "total_flights",
            "cancelled_flights",
            "cancellation_rate_pct",
        }
        self.assertTrue(expected_keys.issubset(set(row.keys())))

    @patch("app.routes.ops.get_passenger_impact_summary")
    def test_passenger_impact_summary_contract(self, mock_repo):
        mock_repo.return_value = {
            "total_itineraries": 2800,
            "impacted_itineraries": 530,
            "impact_rate_pct": 18.93,
            "connection_risk_count": 146,
            "top_impacted_flights": [
                {
                    "flight_id": "AA1234",
                    "impacted_itineraries": 34,
                }
            ],
        }

        response = client.get("/ops/passenger-impact-summary")
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        expected_keys = {
            "total_itineraries",
            "impacted_itineraries",
            "impact_rate_pct",
            "connection_risk_count",
            "top_impacted_flights",
        }
        self.assertTrue(expected_keys.issubset(set(payload.keys())))
        self.assertIsInstance(payload["top_impacted_flights"], list)

    @patch("app.routes.ops.get_latest_metrics_snapshot")
    def test_latest_metrics_snapshot_contract(self, mock_repo):
        mock_repo.return_value = {
            "_id": "abc123",
            "snapshot_id": "snapshot_20260526_001",
            "created_at": "2026-05-26T00:00:00",
            "source": "mongodb_operational_collections",
            "metrics": {
                "total_flights": 10000,
                "delayed_flights": 1466,
            },
            "top_delayed_routes": [],
            "cancellations_by_airport": [],
            "passenger_impact_summary": {},
        }

        response = client.get("/ops/metrics-snapshots/latest")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("result", payload)
        self.assertIsInstance(payload["result"], dict)
        self.assertIn("snapshot_id", payload["result"])
        self.assertIn("metrics", payload["result"])

    @patch("app.routes.ops.get_metrics_snapshots")
    def test_metrics_snapshots_contract(self, mock_repo):
        mock_repo.return_value = [
            {
                "_id": "abc123",
                "snapshot_id": "snapshot_20260526_001",
                "created_at": "2026-05-26T00:00:00",
                "source": "mongodb_operational_collections",
            }
        ]

        response = client.get("/ops/metrics-snapshots?limit=10")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("limit", payload)
        self.assertIn("results", payload)
        self.assertIsInstance(payload["results"], list)
        self.assertGreaterEqual(len(payload["results"]), 1)
        self.assertIn("snapshot_id", payload["results"][0])


if __name__ == "__main__":
    unittest.main()
