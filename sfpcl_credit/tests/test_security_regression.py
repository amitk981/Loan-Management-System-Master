import base64
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import mock

import jwt
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, SimpleTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.identity.models import Permission, RolePermission
from sfpcl_credit.identity.modules.tokens import encode_token
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.base import IdentityTestCase
from sfpcl_credit.security_regression.matrix import (
    CONTROL_MATRIX,
    MatrixValidationError,
    required_control_ids,
    validate_control_matrix,
    validate_test_labels,
)
from sfpcl_credit.security_regression.runner import build_summary
from sfpcl_credit.security_regression.scanners import ScannerSpec, execute_scanner
from sfpcl_credit.security_regression.lane import run_security_regression


class SecurityRegressionCommandTests(SimpleTestCase):
    def test_controlled_failure_is_nonzero_and_names_exact_control(self):
        with TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "security-summary.json"

            with self.assertRaisesMessage(CommandError, "SEC-AUTH-001"):
                call_command(
                    "security_regression",
                    output=output_path,
                    force_failure="SEC-AUTH-001",
                )

            summary = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["result"], "fail")
            self.assertEqual(summary["failing_controls"], ["SEC-AUTH-001"])

    def test_green_summary_has_deterministic_counts_versions_skips_and_hash(self):
        summary = build_summary(
            control_results=[
                {"control_id": "SEC-AUTH-001", "status": "pass"},
                {"control_id": "SEC-AUTH-002", "status": "pass"},
                {
                    "control_id": "SEC-AUTH-003",
                    "status": "skip",
                    "reason": "phase-2-mfa",
                },
            ],
            scanner_results=[
                {
                    "scanner": "detect-secrets",
                    "version": "1.5.0",
                    "status": "pass",
                },
                {
                    "scanner": "pip-audit",
                    "version": "2.10.1",
                    "status": "pass",
                },
            ],
            approved_skip_reasons={"phase-2-mfa"},
        )

        self.assertEqual(summary["result"], "pass")
        self.assertEqual(summary["counts"], {"pass": 2, "fail": 0, "skip": 1})
        self.assertEqual(
            summary["skips"],
            [{"control_id": "SEC-AUTH-003", "reason": "phase-2-mfa"}],
        )
        self.assertEqual(
            summary["scanner_versions"],
            {"detect-secrets": "1.5.0", "pip-audit": "2.10.1"},
        )
        summary_without_hash = {**summary}
        actual_hash = summary_without_hash.pop("summary_sha256")
        canonical = json.dumps(
            summary_without_hash,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        self.assertEqual(actual_hash, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(
            build_summary(
                control_results=[
                    {"control_id": "SEC-AUTH-001", "status": "pass"},
                    {"control_id": "SEC-AUTH-002", "status": "pass"},
                    {
                        "control_id": "SEC-AUTH-003",
                        "status": "skip",
                        "reason": "phase-2-mfa",
                    },
                ],
                scanner_results=[
                    {
                        "scanner": "detect-secrets",
                        "version": "1.5.0",
                        "status": "pass",
                    },
                    {
                        "scanner": "pip-audit",
                        "version": "2.10.1",
                        "status": "pass",
                    },
                ],
                approved_skip_reasons={"phase-2-mfa"},
            ),
            summary,
        )

    def test_control_matrix_contains_every_source_control_exactly_once(self):
        validated = validate_control_matrix(CONTROL_MATRIX)

        self.assertEqual(
            [control["control_id"] for control in validated],
            sorted(required_control_ids()),
        )
        for control in validated:
            self.assertTrue(
                control.get("test_labels") or control.get("blocking_finding"),
                control["control_id"],
            )

        duplicate = [*CONTROL_MATRIX, CONTROL_MATRIX[0]]
        with self.assertRaisesMessage(MatrixValidationError, "duplicate"):
            validate_control_matrix(duplicate)

        with self.assertRaisesMessage(MatrixValidationError, "missing"):
            validate_control_matrix(CONTROL_MATRIX[1:])

        unknown = [
            *CONTROL_MATRIX,
            {"control_id": "SEC-UNKNOWN-999", "test_labels": ["example"]},
        ]
        with self.assertRaisesMessage(MatrixValidationError, "unknown"):
            validate_control_matrix(unknown)

    def test_every_matrix_test_label_resolves_to_a_real_behavior_test(self):
        self.assertEqual(validate_test_labels(CONTROL_MATRIX), ())

    def test_required_scanner_unavailability_and_findings_fail_without_raw_output(self):
        specification = ScannerSpec(
            name="synthetic-scanner",
            expected_version="1.2.3",
            version_command=("synthetic-scanner", "--version"),
            scan_command=("synthetic-scanner", "--json"),
        )

        def unavailable(*args, **kwargs):
            raise FileNotFoundError("synthetic-scanner")

        unavailable_result = execute_scanner(
            specification,
            cwd=Path.cwd(),
            run=unavailable,
        )
        self.assertEqual(
            unavailable_result,
            {
                "scanner": "synthetic-scanner",
                "version": "unavailable",
                "status": "fail",
                "error_code": "SCANNER_UNAVAILABLE",
                "finding_count": 0,
                "report_sha256": hashlib.sha256(b"").hexdigest(),
            },
        )

        raw_sensitive_output = (
            '{"findings":[{"token":"eyJhbGciOiJIUzI1NiJ9.'
            'eyJzdWIiOiIxIn0.signature","pan":"ABCDE1234F"}]}'
        )
        calls = iter(
            [
                subprocess.CompletedProcess(
                    args=specification.version_command,
                    returncode=0,
                    stdout="synthetic-scanner 1.2.3\n",
                    stderr="",
                ),
                subprocess.CompletedProcess(
                    args=specification.scan_command,
                    returncode=1,
                    stdout=raw_sensitive_output,
                    stderr="",
                ),
            ]
        )
        finding_result = execute_scanner(
            specification,
            cwd=Path.cwd(),
            run=lambda *args, **kwargs: next(calls),
        )
        self.assertEqual(finding_result["status"], "fail")
        self.assertEqual(finding_result["error_code"], "SCANNER_FINDINGS")
        self.assertEqual(finding_result["version"], "1.2.3")
        serialized = json.dumps(finding_result)
        self.assertNotIn("ABCDE1234F", serialized)
        self.assertNotIn("eyJhbGciOiJIUzI1NiJ9", serialized)
        self.assertRegex(finding_result["report_sha256"], r"^[0-9a-f]{64}$")

        mismatch = execute_scanner(
            specification,
            cwd=Path.cwd(),
            run=lambda *args, **kwargs: subprocess.CompletedProcess(
                args=specification.version_command,
                returncode=0,
                stdout="synthetic-scanner 9.9.9\n",
                stderr="",
            ),
        )
        self.assertEqual(mismatch["status"], "fail")
        self.assertEqual(mismatch["error_code"], "SCANNER_VERSION_MISMATCH")

    def test_lane_reports_exact_blocking_controls_with_green_checks_and_scanners(self):
        def fake_run(command, **kwargs):
            command_text = " ".join(str(part) for part in command)
            environment = kwargs.get("env", {})
            if " manage.py test " in f" {command_text} ":
                return subprocess.CompletedProcess(command, 0, "OK\n", "")
            if command[-2:] == ["-c", command[-1]]:
                required = {
                    "SFPCL_SECRET_KEY",
                    "SFPCL_JWT_SIGNING_KEY",
                    "SFPCL_ALLOWED_HOSTS",
                    "SFPCL_CORS_ORIGINS",
                    "SFPCL_CSRF_TRUSTED_ORIGINS",
                    "SFPCL_FIELD_LOOKUP_KEY",
                }
                return subprocess.CompletedProcess(
                    command,
                    0 if required.issubset(environment) else 1,
                    "",
                    "",
                )
            if "--version" in command:
                if any("detect-secrets" in str(part) for part in command):
                    version_output = "detect-secrets 1.5.0\n"
                elif "pip_audit" in command:
                    version_output = "pip-audit 2.10.1\n"
                else:
                    version_output = "10.8.2\n"
                return subprocess.CompletedProcess(
                    command,
                    0,
                    version_output,
                    "",
                )
            if any("detect-secrets" in str(part) for part in command):
                output = '{"results":{}}'
            elif "pip_audit" in command:
                output = "[]"
            else:
                output = '{"metadata":{"vulnerabilities":{"high":0,"critical":0}}}'
            return subprocess.CompletedProcess(command, 0, output, "")

        summary = run_security_regression(run=fake_run)

        self.assertEqual(summary["result"], "fail")
        self.assertEqual(
            summary["failing_controls"],
            [
                "SEC-AUTH-010",
                "SEC-WEB-004",
                "SEC-WEB-005",
            ],
        )
        self.assertEqual(summary["failing_scanners"], [])
        self.assertEqual(summary["failing_checks"], [])
        self.assertEqual(summary["counts"], {"pass": 52, "fail": 3, "skip": 0})


class ProductionSettingsSecurityTests(SimpleTestCase):
    def test_production_boot_rejects_missing_or_insecure_security_configuration(self):
        valid_environment = {
            "SFPCL_DEPLOYMENT_ENVIRONMENT": "production",
            "SFPCL_SECRET_KEY": "synthetic-production-django-key-32",
            "SFPCL_JWT_SIGNING_KEY": "synthetic-production-jwt-key-value",
            "SFPCL_ALLOWED_HOSTS": "credit.example.test",
            "SFPCL_CORS_ORIGINS": "https://lms.example.test",
            "SFPCL_CSRF_TRUSTED_ORIGINS": "https://lms.example.test",
            "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION": "prod-v1",
            "SFPCL_FIELD_ENCRYPTION_KEY_REF": "vault:test/prod-v1",
            "SFPCL_FIELD_ENCRYPTION_KEYS": json.dumps(
                {
                    "prod-v1": base64.urlsafe_b64encode(b"P" * 32).decode(
                        "ascii"
                    )
                }
            ),
            "SFPCL_FIELD_LOOKUP_KEY": base64.urlsafe_b64encode(
                b"H" * 32
            ).decode("ascii"),
        }

        valid = self._production_probe(valid_environment)
        self.assertEqual(valid.returncode, 0, valid.stderr)

        invalid_cases = {
            "SFPCL_SECRET_KEY": None,
            "SFPCL_JWT_SIGNING_KEY": None,
            "SFPCL_ALLOWED_HOSTS": "*",
            "SFPCL_CORS_ORIGINS": "http://lms.example.test",
            "SFPCL_CSRF_TRUSTED_ORIGINS": "http://lms.example.test",
        }
        for variable, unsafe_value in invalid_cases.items():
            with self.subTest(variable=variable):
                environment = {**valid_environment}
                if unsafe_value is None:
                    environment.pop(variable)
                else:
                    environment[variable] = unsafe_value
                result = self._production_probe(environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(variable, result.stderr)

        reused_secret = {
            **valid_environment,
            "SFPCL_JWT_SIGNING_KEY": valid_environment["SFPCL_SECRET_KEY"],
        }
        result = self._production_probe(reused_secret)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be separate", result.stderr)

    @staticmethod
    def _production_probe(environment):
        clean_environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("SFPCL_")
        }
        return subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from sfpcl_credit.config import production_settings as s;"
                    "assert s.DEBUG is False;"
                    "assert s.JWT_SIGNING_KEY != s.SECRET_KEY;"
                    "assert s.SECURE_SSL_REDIRECT is True;"
                    "assert s.SESSION_COOKIE_SECURE is True;"
                    "assert s.CSRF_COOKIE_SECURE is True;"
                    "assert s.SECURE_HSTS_SECONDS > 0;"
                    "assert s.ENABLE_DEMO_SURFACES is False"
                ),
            ],
            env={**clean_environment, **environment},
            capture_output=True,
            text=True,
            check=False,
        )

    @override_settings(
        JWT_SIGNING_KEY="synthetic-dedicated-jwt-signing-key",
        SECRET_KEY="synthetic-independent-django-key",
    )
    def test_tokens_use_the_dedicated_signing_key_when_configured(self):
        token = encode_token(
            {
                "token_type": "access",
                "exp": int(
                    (timezone.now() + timezone.timedelta(minutes=1)).timestamp()
                ),
            }
        )

        claims = jwt.decode(
            token,
            "synthetic-dedicated-jwt-signing-key",
            algorithms=["HS256"],
        )
        self.assertEqual(claims["token_type"], "access")
        with self.assertRaises(jwt.InvalidSignatureError):
            jwt.decode(
                token,
                "synthetic-independent-django-key",
                algorithms=["HS256"],
            )


class SecurityBoundaryRegressionTests(IdentityTestCase):
    def test_unknown_and_known_login_failures_use_the_same_public_error(self):
        known = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": self.user.email,
                "password": "SyntheticWrongPassword!",
            },
            content_type="application/json",
        )
        unknown = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": "unknown.user@example.test",
                "password": "SyntheticWrongPassword!",
            },
            content_type="application/json",
        )

        self.assertEqual(known.status_code, 401)
        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(known.json()["error"], unknown.json()["error"])

    def test_unknown_permission_and_admin_without_business_role_are_denied(self):
        self.role.role_code = "system_admin"
        self.role.role_name = "System Administrator"
        self.role.save(update_fields=["role_code", "role_name"])
        unknown_permission = Permission.objects.create(
            permission_code="unknown.future.capability",
            permission_name="Unknown future capability",
            module_name="unknown",
            risk_level="high",
        )
        RolePermission.objects.create(
            role=self.role,
            permission=unknown_permission,
        )

        response = Client().post(
            "/api/v1/members/",
            data={
                "member_type": "individual_farmer",
                "legal_name": "Synthetic denied member",
            },
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "FORBIDDEN")
        self.assertEqual(Member.objects.count(), 0)

    def test_search_injection_is_data_not_executable_syntax(self):
        self._grant("members.member.read")

        response = Client().get(
            "/api/v1/members/",
            data={"search": "' OR 1=1; DROP TABLE members_member; --"},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"], [])
        self.assertEqual(Member.objects.count(), 0)

    def test_untrusted_text_is_json_escaped_and_never_rendered_as_html(self):
        self._grant("members.member.read")
        untrusted_text = '<script>alert("synthetic")</script>'

        response = Client().get(
            "/api/v1/members/",
            data={"search": untrusted_text},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["data"], [])
        self.assertNotIn("text/html", response["Content-Type"])
        self.assertNotIn("<script>", response.content.decode("utf-8"))

    def test_unapproved_cors_origin_receives_no_allow_header(self):
        response = Client().get(
            "/api/v1/health/live/",
            headers={"Origin": "https://unapproved.example.test"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Access-Control-Allow-Origin", response)

    @override_settings(DEBUG=False)
    def test_production_error_response_never_contains_traceback(self):
        self._grant("members.member.read")

        response = Client().get(
            "/api/v1/members/",
            data={"limit": "not-an-integer"},
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)
        body = response.content.decode("utf-8")
        self.assertNotIn("Traceback", body)
        self.assertNotIn(str(Path.cwd()), body)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_logs_errors_and_urls_do_not_contain_sensitive_fixtures(self):
        synthetic_token = "synthetic.header.payload.signature"
        with mock.patch("logging.Logger._log") as log_call:
            response = Client().get(
                "/api/v1/auth/me/",
                headers={"Authorization": f"Bearer {synthetic_token}"},
            )

        self.assertEqual(response.status_code, 401)
        inspected = json.dumps(
            {
                "body": response.json(),
                "path": response.request["PATH_INFO"],
                "logs": [str(call) for call in log_call.call_args_list],
            }
        )
        self.assertNotIn(synthetic_token, inspected)
        self.assertNotIn("Authorization", inspected)

    def _grant(self, permission_code):
        permission = Permission.objects.create(
            permission_code=permission_code,
            permission_name=permission_code,
            module_name=permission_code.split(".", 1)[0],
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.role, permission=permission)

    def _auth_headers(self):
        response = Client().post(
            "/api/v1/auth/login/",
            data={
                "email": self.user.email,
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return {
            "Authorization": (
                f"Bearer {response.json()['data']['access_token']}"
            )
        }
