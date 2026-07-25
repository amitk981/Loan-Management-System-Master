import json
import os
from io import StringIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.core.management import CommandError, call_command
from django.test import LiveServerTestCase, SimpleTestCase

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.deployment_smoke import REQUIRED_SMOKE_PERMISSIONS
from sfpcl_credit.identity.models import (
    Permission,
    Role,
    RolePermission,
    User,
)
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.members.models import Member


class JsonResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return self.payload.encode("utf-8")


def smoke_identity_response(*, role_codes=None, permissions=None):
    return JsonResponse(
        json.dumps(
            {
                "success": True,
                "data": {
                    "email": "smoke.reader@sfpcl.example",
                    "role_codes": role_codes or ["deployment_smoke_reader"],
                    "permissions": sorted(
                        permissions
                        if permissions is not None
                        else REQUIRED_SMOKE_PERMISSIONS
                    ),
                },
            }
        )
    )


class SmokeCheckCommandTests(SimpleTestCase):
    @patch(
        "urllib.request.urlopen",
        side_effect=URLError("synthetic target unavailable"),
    )
    def test_smoke_check_fails_legibly_when_liveness_is_unreachable(
        self,
        _urlopen,
    ):
        with patch.dict(
            os.environ,
            {
                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
            },
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Smoke check failed at liveness: target is unreachable",
            ):
                call_command(
                    "smoke_check",
                    base_url="https://staging.example.test",
                )

    @patch(
        "urllib.request.urlopen",
        side_effect=[
            JsonResponse('{"status":"live"}'),
            HTTPError(
                "https://staging.example.test/health/ready/",
                503,
                "Service Unavailable",
                {},
                None,
            ),
        ],
    )
    def test_smoke_check_fails_legibly_when_readiness_is_not_ready(
        self,
        _urlopen,
    ):
        with patch.dict(
            os.environ,
            {
                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
            },
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Smoke check failed at readiness: target returned HTTP 503",
            ):
                call_command(
                    "smoke_check",
                    base_url="https://staging.example.test/",
                )

    @patch(
        "urllib.request.urlopen",
        side_effect=[
            JsonResponse('{"status":"live"}'),
            JsonResponse('{"status":"ready"}'),
            HTTPError(
                "https://staging.example.test/api/v1/auth/login/",
                401,
                "Unauthorized",
                {},
                None,
            ),
        ],
    )
    def test_smoke_check_fails_legibly_when_authentication_fails(
        self,
        _urlopen,
    ):
        with patch.dict(
            os.environ,
            {
                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
            },
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Smoke check failed at authentication: target returned HTTP 401",
            ):
                call_command(
                    "smoke_check",
                    base_url="https://staging.example.test",
                )

    @patch(
        "urllib.request.urlopen",
        side_effect=[
            JsonResponse('{"status":"live"}'),
            JsonResponse('{"status":"ready"}'),
            JsonResponse('{"data":{"access_token":"synthetic-access-token"}}'),
            smoke_identity_response(),
            HTTPError(
                "https://staging.example.test/api/v1/dashboard/",
                500,
                "Server Error",
                {},
                None,
            ),
        ],
    )
    def test_smoke_check_fails_legibly_when_a_workflow_read_fails(
        self,
        _urlopen,
    ):
        with patch.dict(
            os.environ,
            {
                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
            },
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Smoke check failed at workflow dashboard: target returned HTTP 500",
            ):
                call_command(
                    "smoke_check",
                    base_url="https://staging.example.test",
                )

    @patch(
        "urllib.request.urlopen",
        side_effect=[
            JsonResponse('{"status":"live"}'),
            JsonResponse('{"status":"ready"}'),
            JsonResponse('{"data":{"access_token":"synthetic-access-token"}}'),
            JsonResponse('{"success":false}'),
        ],
    )
    def test_smoke_check_fails_when_current_user_round_trip_is_invalid(
        self,
        _urlopen,
    ):
        with patch.dict(
            os.environ,
            {
                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
            },
        ):
            with self.assertRaisesMessage(
                CommandError,
                "account is not the dedicated low-privilege smoke reader",
            ):
                call_command(
                    "smoke_check",
                    base_url="https://staging.example.test",
                )

    @patch(
        "urllib.request.urlopen",
        side_effect=[
            JsonResponse('{"status":"live"}'),
            JsonResponse('{"status":"ready"}'),
            JsonResponse('{"data":{"access_token":"synthetic-access-token"}}'),
            smoke_identity_response(role_codes=["system_admin"]),
        ],
    )
    def test_smoke_check_rejects_an_admin_account(self, _urlopen):
        with patch.dict(
            os.environ,
            {
                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
            },
        ):
            with self.assertRaisesMessage(
                CommandError,
                "account is not the dedicated low-privilege smoke reader",
            ):
                call_command(
                    "smoke_check",
                    base_url="https://staging.example.test",
                )

    def test_smoke_check_passes_using_only_authentication_and_read_requests(self):
        requests = []

        def respond(request, timeout):
            self.assertEqual(timeout, 10)
            requests.append((request.get_method(), request.full_url))
            if request.full_url.endswith("/health/live/"):
                return JsonResponse('{"status":"live"}')
            if request.full_url.endswith("/health/ready/"):
                return JsonResponse('{"status":"ready"}')
            if request.full_url.endswith("/api/v1/auth/login/"):
                return JsonResponse(
                    '{"success":true,"data":{"access_token":"synthetic-access-token"}}'
                )
            if request.full_url.endswith("/api/v1/auth/me/"):
                return smoke_identity_response()
            if request.full_url.endswith("/api/v1/dashboard/"):
                return JsonResponse('{"success":true,"data":{"cards":[]}}')
            return JsonResponse(
                '{"success":true,"data":[],"pagination":'
                '{"page":1,"page_size":1,"total_count":0,"total_pages":0,'
                '"has_next":false,"has_previous":false}}'
            )

        stdout = StringIO()
        password = "SyntheticPassword123!"
        with patch("urllib.request.urlopen", side_effect=respond):
            with patch.dict(
                os.environ,
                {
                    "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                    "SFPCL_SMOKE_CHECK_PASSWORD": password,
                },
            ):
                call_command(
                    "smoke_check",
                    base_url="https://staging.example.test/",
                    stdout=stdout,
                )

        self.assertEqual(
            [request for request in requests if request[0] == "POST"],
            [
                (
                    "POST",
                    "https://staging.example.test/api/v1/auth/login/",
                )
            ],
        )
        self.assertTrue(
            all(
                method == "GET"
                for method, url in requests
                if not url.endswith("/api/v1/auth/login/")
            )
        )
        self.assertIn(
            "Smoke check passed: 8 read-only workflows",
            stdout.getvalue(),
        )
        self.assertNotIn(password, stdout.getvalue())


class SmokeCheckLocalServerTests(LiveServerTestCase):
    static_handler = staticmethod(lambda application: application)

    def setUp(self):
        role = Role.objects.create(
            role_code="deployment_smoke_reader",
            role_name="Deployment Smoke Reader",
            description="Dedicated low-privilege deployment smoke role.",
            is_system_role=False,
            status="active",
        )
        user = User.objects.create(
            full_name="Deployment Smoke Reader",
            email="smoke.reader@sfpcl.example",
            primary_role=role,
            status="active",
        )
        user.set_password("SyntheticPassword123!")
        user.save()
        for permission_code in sorted(REQUIRED_SMOKE_PERMISSIONS):
            permission, _created = Permission.objects.get_or_create(
                permission_code=permission_code,
                defaults={
                    "permission_name": permission_code,
                    "module_name": permission_code.split(".", 1)[0],
                    "risk_level": Permission.RISK_MEDIUM,
                },
            )
            RolePermission.objects.create(role=role, permission=permission)

    def test_smoke_check_against_local_server_does_not_write_business_records(
        self,
    ):
        business_counts_before = self._business_counts()
        stdout = StringIO()

        with patch.dict(
            os.environ,
            {
                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
            },
        ):
            call_command(
                "smoke_check",
                base_url=self.live_server_url,
                stdout=stdout,
            )

        self.assertEqual(self._business_counts(), business_counts_before)
        self.assertIn(
            "Smoke check passed: 8 read-only workflows",
            stdout.getvalue(),
        )

    @staticmethod
    def _business_counts():
        return {
            "members": Member.objects.count(),
            "applications": LoanApplication.objects.count(),
            "approval_cases": ApprovalCase.objects.count(),
            "loan_accounts": LoanAccount.objects.count(),
        }
