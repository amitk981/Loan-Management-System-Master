from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from sfpcl_credit.performance_readiness.matrix import (
    PERFORMANCE_SCENARIOS,
    MatrixValidationError,
    required_scenario_ids,
    validate_scenario_matrix,
)
from sfpcl_credit.performance_readiness.runner import (
    EvidenceValidationError,
    build_performance_summary,
)
from sfpcl_credit.performance_readiness.local import run_bounded_local
from sfpcl_credit.performance_readiness.probes import validate_probe_outcome


class PerformanceReadinessContractTests(SimpleTestCase):
    def test_matrix_requires_every_load_target_and_resilience_scenario_once(self):
        validated = validate_scenario_matrix(PERFORMANCE_SCENARIOS)

        self.assertEqual(
            [scenario["scenario_id"] for scenario in validated],
            sorted(required_scenario_ids()),
        )

        with self.assertRaisesMessage(MatrixValidationError, "missing scenarios"):
            validate_scenario_matrix(PERFORMANCE_SCENARIOS[1:])

        with self.assertRaisesMessage(MatrixValidationError, "duplicate scenarios"):
            validate_scenario_matrix(
                (*PERFORMANCE_SCENARIOS, PERFORMANCE_SCENARIOS[0])
            )

    def test_summary_rejects_a_missing_mandatory_scenario(self):
        results = [
            self._result(scenario)
            for scenario in validate_scenario_matrix(PERFORMANCE_SCENARIOS)
        ]

        with self.assertRaisesMessage(
            EvidenceValidationError,
            "missing results",
        ):
            build_performance_summary(
                scenario_results=results[1:],
                environment=self._environment(),
                expected_commit="a" * 40,
            )

    def test_summary_computes_a_controlled_latency_failure(self):
        scenarios = validate_scenario_matrix(PERFORMANCE_SCENARIOS)
        results = [self._result(scenario) for scenario in scenarios]
        login = next(
            result
            for result in results
            if result["scenario_id"] == "TARGET-LOGIN"
        )
        login["samples"] = [1.8, 2.2, 2.4]
        login["status"] = "pass"
        login["raw_result_sha256"] = self._raw_result_hash(login)

        summary = build_performance_summary(
            scenario_results=results,
            environment=self._environment(),
            expected_commit="a" * 40,
        )

        self.assertEqual(summary["result"], "fail")
        self.assertEqual(summary["failing_scenarios"], ["TARGET-LOGIN"])
        evaluated = next(
            row
            for row in summary["scenarios"]
            if row["scenario_id"] == "TARGET-LOGIN"
        )
        self.assertEqual(evaluated["status"], "fail")
        self.assertEqual(evaluated["observed"]["p95"], 2.4)

    def test_summary_rejects_an_unsupported_skip(self):
        scenarios = validate_scenario_matrix(PERFORMANCE_SCENARIOS)
        results = [self._result(scenario) for scenario in scenarios]
        results[0]["status"] = "skip"
        results[0]["reason"] = "local service unavailable"

        with self.assertRaisesMessage(
            EvidenceValidationError,
            "unsupported status",
        ):
            build_performance_summary(
                scenario_results=results,
                environment=self._environment(),
                expected_commit="a" * 40,
            )

    def test_matrix_rejects_a_malformed_threshold(self):
        malformed = deepcopy(PERFORMANCE_SCENARIOS)
        malformed[0]["threshold"]["value"] = "two seconds"

        with self.assertRaisesMessage(
            MatrixValidationError,
            "malformed thresholds",
        ):
            validate_scenario_matrix(malformed)

    def test_summary_rejects_wrong_commit_evidence(self):
        scenarios = validate_scenario_matrix(PERFORMANCE_SCENARIOS)

        with self.assertRaisesMessage(
            EvidenceValidationError,
            "commit mismatch",
        ):
            build_performance_summary(
                scenario_results=[
                    self._result(scenario) for scenario in scenarios
                ],
                environment=self._environment(),
                expected_commit="c" * 40,
            )

    def test_summary_rejects_stale_evidence(self):
        scenarios = validate_scenario_matrix(PERFORMANCE_SCENARIOS)

        with self.assertRaisesMessage(
            EvidenceValidationError,
            "stale evidence",
        ):
            build_performance_summary(
                scenario_results=[
                    self._result(scenario) for scenario in scenarios
                ],
                environment=self._environment(),
                expected_commit="a" * 40,
                now=datetime(2026, 7, 24, 14, 0, tzinfo=timezone.utc),
                max_age_seconds=3600,
            )

    def test_command_writes_controlled_failure_and_returns_nonzero(self):
        scenarios = validate_scenario_matrix(PERFORMANCE_SCENARIOS)
        results = [self._result(scenario) for scenario in scenarios]
        results[0]["status"] = "fail"
        results[0]["raw_result_sha256"] = self._raw_result_hash(results[0])

        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            results_path = root / "results.json"
            environment_path = root / "environment.json"
            output_path = root / "summary.json"
            results_path.write_text(json.dumps(results), encoding="utf-8")
            environment_path.write_text(
                json.dumps(self._environment()),
                encoding="utf-8",
            )

            with self.assertRaisesMessage(CommandError, "PERF-001"):
                call_command(
                    "performance_readiness",
                    results=results_path,
                    environment=environment_path,
                    output=output_path,
                    expected_commit="a" * 40,
                )

            summary = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["result"], "fail")
            self.assertEqual(summary["failing_scenarios"], ["PERF-001"])

    def test_summary_rejects_credentials_and_pii_in_environment_facts(self):
        scenarios = validate_scenario_matrix(PERFORMANCE_SCENARIOS)
        unsafe = {
            **self._environment(),
            "credentials": {"password": "not-safe-to-retain"},
        }

        with self.assertRaisesMessage(
            EvidenceValidationError,
            "unsafe environment facts",
        ):
            build_performance_summary(
                scenario_results=[
                    self._result(scenario) for scenario in scenarios
                ],
                environment=unsafe,
                expected_commit="a" * 40,
            )

    def test_summary_rejects_a_tampered_raw_result_hash(self):
        scenarios = validate_scenario_matrix(PERFORMANCE_SCENARIOS)
        results = [self._result(scenario) for scenario in scenarios]
        results[0]["samples"] = [999]

        with self.assertRaisesMessage(
            EvidenceValidationError,
            "raw result hash mismatch",
        ):
            build_performance_summary(
                scenario_results=results,
                environment=self._environment(),
                expected_commit="a" * 40,
            )

    def test_bounded_local_runner_executes_public_behavior_seams_with_warmup(self):
        calls = []

        def successful_test(command, **kwargs):
            calls.append(command)

            class Result:
                returncode = 0
                stdout = "OK"
                stderr = ""

            return Result()

        results = run_bounded_local(
            scenarios=validate_scenario_matrix(PERFORMANCE_SCENARIOS),
            run=successful_test,
        )

        self.assertEqual(
            {result["scenario_id"] for result in results},
            required_scenario_ids(),
        )
        self.assertTrue(
            all(result["samples"] for result in results),
        )
        self.assertTrue(
            any("test_active_user_can_login" in " ".join(call) for call in calls)
        )

    def test_resilience_probes_fail_closed_and_redis_requires_equal_sor_hashes(self):
        invalid = {
            "PROBE-SUSTAINED-WORKFLOW": {},
            "PROBE-LARGE-DOCUMENT-VOLUME": {"storage_stable": False},
            "PROBE-LARGE-AUDIT-TABLE": {"queries_acceptable": False},
            "PROBE-HEAVY-EXPORT-QUEUE": {"api_responsive": False},
            "PROBE-WORKER-RESTART": {"duplicate_outputs": 1},
            "PROBE-REDIS-RESTART": {
                "system_of_record_before_sha256": "a" * 64,
                "system_of_record_after_sha256": "b" * 64,
            },
            "PROBE-DATABASE-PRESSURE": {"controlled_degradation": False},
        }
        for probe_id, outcome in invalid.items():
            with self.subTest(probe_id=probe_id):
                with self.assertRaisesMessage(
                    EvidenceValidationError,
                    probe_id,
                ):
                    validate_probe_outcome(probe_id, outcome)

        digest = "c" * 64
        self.assertEqual(
            validate_probe_outcome(
                "PROBE-REDIS-RESTART",
                {
                    "system_of_record_before_sha256": digest,
                    "system_of_record_after_sha256": digest,
                    "data_loss_count": 0,
                },
            )["status"],
            "pass",
        )

    @staticmethod
    def _result(scenario):
        threshold = scenario["threshold"]
        if threshold["kind"] == "maximum_seconds":
            result = {
                "scenario_id": scenario["scenario_id"],
                "status": "pass",
                "samples": [threshold["value"] / 2],
            }
        else:
            result = {
                "scenario_id": scenario["scenario_id"],
                "status": "release-evidence-required",
                "samples": [0.01],
            }
        result["raw_result_sha256"] = (
            PerformanceReadinessContractTests._raw_result_hash(result)
        )
        return result

    @staticmethod
    def _raw_result_hash(result):
        raw = json.dumps(
            {
                "samples": result["samples"],
                "status": result["status"],
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _environment():
        return {
            "environment_id": "local-bounded-sqlite",
            "environment_class": "bounded-local",
            "commit": "a" * 40,
            "generated_at": "2026-07-24T12:00:00Z",
            "seed": 1202,
            "dataset_counts": {"synthetic_members": 100},
            "tool_versions": {"python": "3.11", "django": "5.2"},
        }
