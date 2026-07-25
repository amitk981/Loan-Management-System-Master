import json
import os
import urllib.request
from urllib.error import HTTPError, URLError

from django.core.management.base import BaseCommand, CommandError

from sfpcl_credit.deployment_smoke import (
    WORKFLOW_READS,
    validate_smoke_identity,
)


class SmokeCheckFailure(RuntimeError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(message)


class Command(BaseCommand):
    help = "Run read-only post-deployment smoke checks against an environment URL."

    def add_arguments(self, parser):
        parser.add_argument("--base-url", required=True)

    def handle(self, *args, **options):
        base_url = options["base_url"].rstrip("/")
        try:
            self._expect_status(
                f"{base_url}/health/live/",
                stage="liveness",
                expected_status="live",
            )
            self.stdout.write("PASS liveness")
            self._expect_status(
                f"{base_url}/health/ready/",
                stage="readiness",
                expected_status="ready",
            )
            self.stdout.write("PASS readiness")
            access_token, expected_email = self._authenticate(base_url)
            identity = self._request_json(
                f"{base_url}/api/v1/auth/me/",
                stage="authentication",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if not validate_smoke_identity(identity, expected_email):
                raise SmokeCheckFailure(
                    "authentication",
                    "account is not the dedicated low-privilege smoke reader",
                )
            self.stdout.write("PASS authentication")
            self._run_workflow_reads(base_url, access_token)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Smoke check passed: {len(WORKFLOW_READS)} "
                    "read-only workflows"
                )
            )
        except SmokeCheckFailure as error:
            raise CommandError(
                f"Smoke check failed at {error.stage}: {error}"
            ) from error

    def _expect_status(self, url, *, stage, expected_status):
        payload = self._request_json(url, stage=stage)
        if payload != {"status": expected_status}:
            raise SmokeCheckFailure(
                stage,
                "target returned an invalid response",
            )

    def _authenticate(self, base_url):
        email = os.environ.get("SFPCL_SMOKE_CHECK_EMAIL", "").strip()
        password = os.environ.get("SFPCL_SMOKE_CHECK_PASSWORD", "")
        if not email or not password:
            raise SmokeCheckFailure(
                "authentication",
                "smoke-test credentials are not configured",
            )
        payload = self._request_json(
            f"{base_url}/api/v1/auth/login/",
            stage="authentication",
            method="POST",
            body={"email": email, "password": password},
        )
        try:
            access_token = payload["data"]["access_token"]
        except (KeyError, TypeError):
            raise SmokeCheckFailure(
                "authentication",
                "target returned an invalid response",
            )
        if not isinstance(access_token, str) or not access_token:
            raise SmokeCheckFailure(
                "authentication",
                "target returned an invalid response",
            )
        return access_token, email

    def _run_workflow_reads(self, base_url, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        for name, path, requires_pagination in WORKFLOW_READS:
            stage = f"workflow {name}"
            payload = self._request_json(
                f"{base_url}{path}",
                stage=stage,
                headers=headers,
            )
            if not isinstance(payload, dict) or payload.get("success") is not True:
                raise SmokeCheckFailure(
                    stage,
                    "target returned an invalid response",
                )
            if requires_pagination and not isinstance(
                payload.get("pagination"),
                dict,
            ):
                raise SmokeCheckFailure(
                    stage,
                    "target returned an unpaginated response",
                )
            self.stdout.write(f"PASS {stage}")

    @staticmethod
    def _request_json(url, *, stage, method="GET", body=None, headers=None):
        encoded_body = None
        request_headers = {"Accept": "application/json", **(headers or {})}
        if body is not None:
            encoded_body = json.dumps(body).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            url,
            data=encoded_body,
            headers=request_headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise SmokeCheckFailure(
                stage,
                f"target returned HTTP {error.code}",
            ) from error
        except URLError as error:
            raise SmokeCheckFailure(
                stage,
                "target is unreachable",
            ) from error
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SmokeCheckFailure(
                stage,
                "target returned invalid JSON",
            ) from error
