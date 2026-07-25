import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError

from sfpcl_credit.performance_readiness.release_admission import (
    ReleaseEvidenceAdmissionError,
    admit_release_evidence,
)


class Command(BaseCommand):
    help = (
        "Admit exact-candidate environment soak/stress release evidence."
    )

    def add_arguments(self, parser):
        parser.add_argument("--bundle", type=Path, required=True)
        parser.add_argument("--raw-root", type=Path, required=True)
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--expected-commit", required=True)
        parser.add_argument("--expected-environment", required=True)
        parser.add_argument(
            "--agreed-thresholds",
            type=Path,
            required=True,
        )
        parser.add_argument(
            "--expected-thresholds-sha256",
            required=True,
        )
        parser.add_argument(
            "--max-age-seconds",
            type=int,
            default=86400,
        )

    def handle(self, *args, **options):
        try:
            bundle = self._read_bundle(options["bundle"])
            agreed_thresholds = self._read_agreed_thresholds(
                options["agreed_thresholds"],
                expected_sha256=options[
                    "expected_thresholds_sha256"
                ],
                expected_commit=options["expected_commit"],
                expected_environment=options["expected_environment"],
            )
            summary = admit_release_evidence(
                bundle=bundle,
                raw_root=options["raw_root"],
                expected_commit=options["expected_commit"],
                expected_environment=options["expected_environment"],
                agreed_thresholds=agreed_thresholds,
                now=datetime.now(timezone.utc),
                max_age_seconds=options["max_age_seconds"],
            )
        except ReleaseEvidenceAdmissionError as error:
            raise CommandError(str(error)) from error

        output = options["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.stdout.write(
            "release_evidence_admission "
            f"result={summary['result']} "
            f"sha256={summary['summary_sha256']}"
        )

    @staticmethod
    def _read_bundle(path):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ReleaseEvidenceAdmissionError(
                f"invalid release evidence bundle: {path.name}"
            ) from error
        if not isinstance(payload, dict):
            raise ReleaseEvidenceAdmissionError(
                f"invalid release evidence bundle: {path.name}"
            )
        return payload

    @staticmethod
    def _read_agreed_thresholds(
        path,
        *,
        expected_sha256,
        expected_commit,
        expected_environment,
    ):
        try:
            content = path.read_bytes()
            payload = json.loads(content)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ReleaseEvidenceAdmissionError(
                f"invalid agreed threshold manifest: {path.name}"
            ) from error
        digest = hashlib.sha256(content).hexdigest()
        if digest != expected_sha256:
            raise ReleaseEvidenceAdmissionError(
                "agreed threshold manifest hash mismatch"
            )
        if (
            not isinstance(payload, dict)
            or payload.get("schema_version") != 1
            or payload.get("commit") != expected_commit
            or payload.get("environment_id") != expected_environment
            or not isinstance(payload.get("thresholds"), dict)
        ):
            raise ReleaseEvidenceAdmissionError(
                "agreed threshold manifest identity mismatch"
            )
        return payload["thresholds"]
