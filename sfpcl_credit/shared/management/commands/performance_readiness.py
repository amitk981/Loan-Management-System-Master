import json
import os
from pathlib import Path
import platform
import subprocess
from datetime import datetime, timezone

import django
from django.core.management.base import BaseCommand, CommandError

from sfpcl_credit.performance_readiness.local import run_bounded_local
from sfpcl_credit.performance_readiness.matrix import (
    PERFORMANCE_SCENARIOS,
    PROBE_IDS,
    validate_scenario_matrix,
)
from sfpcl_credit.performance_readiness.probes import validate_probe_outcome
from sfpcl_credit.performance_readiness.runner import (
    EvidenceValidationError,
    build_performance_summary,
)


class Command(BaseCommand):
    help = "Evaluate commit-bound performance-readiness measurements."

    def add_arguments(self, parser):
        parser.add_argument("--results", type=Path)
        parser.add_argument("--environment", type=Path)
        parser.add_argument("--probe-outcomes", type=Path)
        parser.add_argument("--run-local", action="store_true")
        parser.add_argument("--results-output", type=Path)
        parser.add_argument("--environment-output", type=Path)
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--expected-commit", required=True)
        parser.add_argument("--matrix-output", type=Path)
        parser.add_argument("--max-age-seconds", type=int)

    def handle(self, *args, **options):
        try:
            if options["run_local"]:
                if options["results"] or options["environment"]:
                    raise EvidenceValidationError(
                        "--run-local cannot use caller result files"
                    )
                matrix = validate_scenario_matrix(PERFORMANCE_SCENARIOS)
                self._require_current_commit(options["expected_commit"])
                results = run_bounded_local(scenarios=matrix)
                environment = self._local_environment(
                    options["expected_commit"]
                )
                if options["results_output"]:
                    self._write_json(options["results_output"], results)
                if options["environment_output"]:
                    self._write_json(
                        options["environment_output"],
                        environment,
                    )
            else:
                if not options["results"] or not options["environment"]:
                    raise EvidenceValidationError(
                        "--results and --environment are required"
                    )
                results = self._read_json(
                    options["results"],
                    expected_type=list,
                )
                environment = self._read_json(
                    options["environment"],
                    expected_type=dict,
                )
            if options["probe_outcomes"]:
                probe_outcomes = self._read_json(
                    options["probe_outcomes"],
                    expected_type=dict,
                )
                for probe_id in PROBE_IDS:
                    if probe_id not in probe_outcomes:
                        raise EvidenceValidationError(
                            f"missing probe outcome: {probe_id}"
                        )
                    validate_probe_outcome(
                        probe_id,
                        probe_outcomes[probe_id],
                    )
            summary = build_performance_summary(
                scenario_results=results,
                environment=environment,
                expected_commit=options["expected_commit"],
                max_age_seconds=options["max_age_seconds"],
            )
        except EvidenceValidationError as error:
            raise CommandError(str(error)) from error

        if options["matrix_output"]:
            self._write_json(
                options["matrix_output"],
                list(validate_scenario_matrix(PERFORMANCE_SCENARIOS)),
            )
        self._write_json(options["output"], summary)
        self.stdout.write(
            f"performance_readiness result={summary['result']} "
            f"sha256={summary['summary_sha256']}"
        )
        if summary["result"] == "fail":
            raise CommandError(
                "Performance readiness failed: "
                + ", ".join(summary["failing_scenarios"])
            )

    @staticmethod
    def _read_json(path, *, expected_type):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise EvidenceValidationError(
                f"invalid JSON evidence: {path.name}"
            ) from error
        if not isinstance(payload, expected_type):
            raise EvidenceValidationError(
                f"invalid JSON evidence type: {path.name}"
            )
        return payload

    @staticmethod
    def _write_json(path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _require_current_commit(expected_commit):
        process = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[4],
            capture_output=True,
            text=True,
            check=False,
        )
        if (
            process.returncode != 0
            or process.stdout.strip() != expected_commit
        ):
            raise EvidenceValidationError("commit mismatch")

    @staticmethod
    def _local_environment(commit):
        return {
            "environment_id": "ralph-bounded-local",
            "environment_class": "bounded-local-public-behavior-probes",
            "commit": commit,
            "generated_at": datetime.now(timezone.utc).isoformat().replace(
                "+00:00",
                "Z",
            ),
            "seed": 1202,
            "dataset_counts": {
                "mapped_scenarios": len(PERFORMANCE_SCENARIOS),
                "synthetic_fixture_only": 1,
            },
            "tool_versions": {
                "python": platform.python_version(),
                "django": django.get_version(),
            },
            "operating_system": platform.system().lower(),
            "cpu_count": os.cpu_count() or 1,
            "database_engine": "django-isolated-test-database",
        }
