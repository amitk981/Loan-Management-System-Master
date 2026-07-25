from datetime import datetime
from unittest.mock import patch

from django.db import OperationalError
from django.test import Client, TestCase, override_settings


class HealthApiTests(TestCase):
    def test_deployment_liveness_is_minimal_and_does_not_query_database(self):
        with self.assertNumQueries(0):
            response = Client().get("/health/live/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), {"status": "live"})

    def test_deployment_readiness_returns_ready_when_required_checks_pass(self):
        response = Client().get("/health/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ready"})

    @patch(
        "sfpcl_credit.ops.database_check",
        side_effect=OperationalError("password=synthetic-must-not-leak"),
    )
    def test_deployment_readiness_returns_terse_503_when_database_is_unavailable(
        self,
        _database_check,
    ):
        response = Client(raise_request_exception=False).get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "not_ready", "reason": "database_unavailable"},
        )
        self.assertNotIn("synthetic-must-not-leak", response.content.decode())

    @patch(
        "sfpcl_credit.ops.migration_check",
        side_effect=OperationalError("token=synthetic-must-not-leak"),
    )
    def test_deployment_readiness_sanitizes_database_failure_during_migration_check(
        self,
        _migration_check,
    ):
        response = Client(raise_request_exception=False).get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "not_ready", "reason": "database_unavailable"},
        )
        self.assertNotIn("synthetic-must-not-leak", response.content.decode())

    @patch("sfpcl_credit.ops.migration_check", return_value=False)
    def test_deployment_readiness_returns_503_when_migrations_are_pending(
        self,
        _migration_check,
    ):
        response = Client().get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "not_ready", "reason": "migrations_pending"},
        )

    @patch("sfpcl_credit.ops.critical_configuration_check", return_value=False)
    def test_deployment_readiness_returns_503_when_configuration_is_missing(
        self,
        _configuration_check,
    ):
        response = Client().get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "not_ready", "reason": "configuration_missing"},
        )

    @override_settings(FIELD_ENCRYPTION_KEYS={"local-v1": "malformed"})
    def test_deployment_readiness_rejects_malformed_field_key_configuration(
        self,
    ):
        response = Client().get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "not_ready", "reason": "configuration_missing"},
        )

    def test_deployment_health_endpoints_reject_mutating_methods(self):
        for path in ("/health/live/", "/health/ready/"):
            with self.subTest(path=path):
                response = Client().post(path)
                self.assertEqual(response.status_code, 405)

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
