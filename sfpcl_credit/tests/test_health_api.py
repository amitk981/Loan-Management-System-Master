from datetime import datetime

from django.test import Client, SimpleTestCase


class HealthApiTests(SimpleTestCase):
    databases = {"default"}

    def test_liveness_endpoint_returns_standard_success_envelope(self):
        response = Client().get("/api/v1/health/live/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = response.json()

        self.assertEqual(payload["success"], True)
        self.assertEqual(
            payload["data"],
            {
                "status": "live",
                "service": "sfpcl-credit-api",
            },
        )
        self.assertIsNone(payload["meta"]["request_id"])
        datetime.fromisoformat(payload["meta"]["timestamp"].replace("Z", "+00:00"))

    def test_health_endpoints_include_request_id_when_provided(self):
        response = Client().get(
            "/api/v1/health/live/",
            headers={"X-Request-ID": "req-health-001"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["meta"]["request_id"], "req-health-001")

    def test_readiness_endpoint_checks_database_connectivity(self):
        response = Client().get("/api/v1/health/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["data"],
            {
                "status": "ready",
                "service": "sfpcl-credit-api",
                "checks": {
                    "database": "ok",
                },
            },
        )

    def test_deep_health_endpoint_reports_dependency_status(self):
        response = Client().get("/api/v1/health/deep/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["data"],
            {
                "status": "ok",
                "service": "sfpcl-credit-api",
                "checks": {
                    "database": "ok",
                },
            },
        )

    def test_health_endpoints_only_accept_get(self):
        response = Client().post("/api/v1/health/live/")

        self.assertEqual(response.status_code, 405)
