from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from sfpcl_credit.performance_readiness.matrix import (
    PERFORMANCE_SCENARIOS,
    PROBE_IDS,
    validate_scenario_matrix,
)
from sfpcl_credit.performance_readiness.release_admission import (
    ReleaseEvidenceAdmissionError,
    validate_synthetic_release_evidence_fixture,
)


class ReleaseEvidenceAdmissionTests(SimpleTestCase):
    candidate_commit = "a" * 40
    environment_id = "staging-release-candidate"
    now = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)

    def test_admission_rejects_each_missing_soak_scenario(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)

            for probe_id in PROBE_IDS:
                with self.subTest(probe_id=probe_id):
                    incomplete = deepcopy(bundle)
                    incomplete["soak_results"] = [
                        result
                        for result in incomplete["soak_results"]
                        if result["scenario_id"] != probe_id
                    ]

                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        "missing soak results",
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=incomplete,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_complete_synthetic_fixture_is_validated_but_not_admitted(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)

            summary = validate_synthetic_release_evidence_fixture(
                bundle=self._bundle(root),
                raw_root=root,
                expected_commit=self.candidate_commit,
                expected_environment=self.environment_id,
                agreed_thresholds=self._agreed_thresholds(),
                now=self.now,
                max_age_seconds=86400,
            )

        self.assertEqual(summary["result"], "synthetic-validation-pass")
        self.assertFalse(summary["release_ready"])
        self.assertEqual(summary["counts"]["soak_results"], 7)
        self.assertEqual(summary["counts"]["performance_results"], 22)
        self.assertEqual(summary["commit"], self.candidate_commit)
        self.assertEqual(summary["environment_id"], self.environment_id)
        self.assertEqual(
            summary["candidate"]["smoke_result"],
            "pass",
        )
        self.assertEqual(
            summary["dataset_load_manifest"]["load_profile"],
            "test-plan-24.1-24.3",
        )
        self.assertEqual(len(summary["raw_results"]), 30)
        self.assertEqual(len(summary["performance_results"]), 22)
        self.assertEqual(len(summary["soak_results"]), 7)
        self.assertEqual(len(summary["summary_sha256"]), 64)

    def test_admission_rejects_wrong_candidate_commit_or_environment(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)

            for field, value, message in (
                ("commit", "b" * 40, "candidate commit mismatch"),
                ("environment_id", "old-staging", "environment mismatch"),
            ):
                with self.subTest(field=field):
                    mismatched = deepcopy(bundle)
                    mismatched["candidate"][field] = value

                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        message,
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=mismatched,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_sustained_workflow_requires_four_nonoverlapping_real_hours(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            sustained = next(
                result
                for result in bundle["soak_results"]
                if result["scenario_id"] == "PROBE-SUSTAINED-WORKFLOW"
            )
            start = datetime.fromisoformat(
                sustained["intervals"][0]["started_at"]
            )
            invalid_cases = {
                "short": {
                    "intervals": [
                        {
                            "started_at": start.isoformat(),
                            "ended_at": (start + timedelta(hours=3)).isoformat(),
                        }
                    ],
                    "actual_elapsed_seconds": 4 * 60 * 60,
                },
                "clock-reversal": {
                    "intervals": [
                        {
                            "started_at": start.isoformat(),
                            "ended_at": (start - timedelta(seconds=1)).isoformat(),
                        }
                    ],
                    "actual_elapsed_seconds": 4 * 60 * 60,
                },
                "overlap": {
                    "intervals": [
                        {
                            "started_at": start.isoformat(),
                            "ended_at": (start + timedelta(hours=3)).isoformat(),
                        },
                        {
                            "started_at": (start + timedelta(hours=2)).isoformat(),
                            "ended_at": (start + timedelta(hours=4)).isoformat(),
                        },
                    ],
                    "actual_elapsed_seconds": 4 * 60 * 60,
                },
            }
            for name, replacement in invalid_cases.items():
                with self.subTest(name=name):
                    invalid = deepcopy(bundle)
                    invalid_sustained = next(
                        result
                        for result in invalid["soak_results"]
                        if result["scenario_id"]
                        == "PROBE-SUSTAINED-WORKFLOW"
                    )
                    invalid_sustained.update(replacement)

                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        "PROBE-SUSTAINED-WORKFLOW",
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=invalid,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_admission_reconciles_every_012f2_performance_result(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            invalid_cases = {}

            missing = deepcopy(bundle)
            missing["performance_results"] = missing["performance_results"][1:]
            invalid_cases["missing"] = missing

            duplicate = deepcopy(bundle)
            duplicate["performance_results"].append(
                deepcopy(duplicate["performance_results"][0])
            )
            invalid_cases["duplicate"] = duplicate

            unknown = deepcopy(bundle)
            unknown["performance_results"][0]["scenario_id"] = "PERF-999"
            invalid_cases["unknown"] = unknown

            changed_contract = deepcopy(bundle)
            changed_contract["performance_results"][0]["source_load"] = {
                "users": 1
            }
            invalid_cases["changed-contract"] = changed_contract

            threshold_failure = deepcopy(bundle)
            threshold_failure["performance_results"][0][
                "threshold_met"
            ] = False
            invalid_cases["threshold-failure"] = threshold_failure

            for name, invalid in invalid_cases.items():
                with self.subTest(name=name):
                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        "performance",
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=invalid,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_admission_rejects_skip_failure_or_recovery_loss(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            invalid_cases = {}

            skipped = deepcopy(bundle)
            skipped["soak_results"][0]["status"] = "skip"
            invalid_cases["skip"] = skipped

            failed_threshold = deepcopy(bundle)
            failed_threshold["soak_results"][1]["threshold_met"] = False
            invalid_cases["threshold"] = failed_threshold

            worker_loss = deepcopy(bundle)
            next(
                result
                for result in worker_loss["soak_results"]
                if result["scenario_id"] == "PROBE-WORKER-RESTART"
            )["outcome"]["duplicate_outputs"] = 1
            invalid_cases["worker"] = worker_loss

            redis_loss = deepcopy(bundle)
            next(
                result
                for result in redis_loss["soak_results"]
                if result["scenario_id"] == "PROBE-REDIS-RESTART"
            )["outcome"]["data_loss_count"] = 1
            invalid_cases["redis"] = redis_loss

            database_uncontrolled = deepcopy(bundle)
            next(
                result
                for result in database_uncontrolled["soak_results"]
                if result["scenario_id"] == "PROBE-DATABASE-PRESSURE"
            )["outcome"]["controlled_degradation"] = False
            invalid_cases["database"] = database_uncontrolled

            for name, invalid in invalid_cases.items():
                with self.subTest(name=name):
                    with self.assertRaises(ReleaseEvidenceAdmissionError):
                        validate_synthetic_release_evidence_fixture(
                            bundle=invalid,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_admission_rejects_missing_duplicate_or_tampered_raw_results(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            invalid_cases = {}

            missing = deepcopy(bundle)
            missing["raw_results"] = missing["raw_results"][1:]
            invalid_cases["missing"] = missing

            duplicate = deepcopy(bundle)
            duplicate["raw_results"].append(
                deepcopy(duplicate["raw_results"][0])
            )
            invalid_cases["duplicate"] = duplicate

            changed_hash = deepcopy(bundle)
            changed_hash["raw_results"][0]["sha256"] = "f" * 64
            invalid_cases["changed-hash"] = changed_hash

            unsafe_path = deepcopy(bundle)
            unsafe_path["raw_results"][0]["path"] = "../outside.json"
            invalid_cases["unsafe-path"] = unsafe_path

            for name, invalid in invalid_cases.items():
                with self.subTest(name=name):
                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        "raw result",
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=invalid,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_synthetic_pending_or_stale_bundle_is_non_admissible(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            invalid_cases = {}

            authority_mismatch = deepcopy(bundle)
            authority_mismatch["synthetic"] = False
            invalid_cases["authority-mismatch"] = authority_mismatch

            bounded_local = deepcopy(bundle)
            bounded_local["evidence_authority"] = "bounded-local"
            invalid_cases["bounded-local"] = bounded_local

            pending = deepcopy(bundle)
            pending["candidate"]["smoke_result"] = "pending"
            invalid_cases["pending"] = pending

            local_environment = deepcopy(bundle)
            local_environment["candidate"]["environment_class"] = "local"
            invalid_cases["local"] = local_environment

            stale = deepcopy(bundle)
            stale["generated_at"] = (
                self.now - timedelta(days=2)
            ).isoformat()
            invalid_cases["stale"] = stale

            future = deepcopy(bundle)
            future["generated_at"] = (
                self.now + timedelta(seconds=1)
            ).isoformat()
            invalid_cases["future"] = future

            for name, invalid in invalid_cases.items():
                with self.subTest(name=name):
                    with self.assertRaises(ReleaseEvidenceAdmissionError):
                        validate_synthetic_release_evidence_fixture(
                            bundle=invalid,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_admission_rejects_credentials_urls_and_live_pii(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            unsafe_values = {
                "credential": {"access_token": "header.payload.signature"},
                "url": {"report_location": "https://internal.example/results"},
                "email": {"operator": "real.person@example.com"},
                "pan": {"operator_reference": "ABCDE1234F"},
                "aadhaar": {"member_reference": "123456789012"},
            }

            for name, unsafe in unsafe_values.items():
                with self.subTest(name=name):
                    contaminated = deepcopy(bundle)
                    contaminated["dataset_load_manifest"].update(unsafe)

                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        "sensitive evidence",
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=contaminated,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_management_command_is_nonzero_for_non_admissible_evidence(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            bundle["synthetic"] = True
            bundle_path = root / "bundle.json"
            thresholds_path = root / "agreed-thresholds.json"
            output_path = root / "summary.json"
            bundle_path.write_text(
                json.dumps(bundle),
                encoding="utf-8",
            )
            threshold_content = json.dumps(
                {
                    "schema_version": 1,
                    "commit": self.candidate_commit,
                    "environment_id": self.environment_id,
                    "thresholds": self._agreed_thresholds(),
                },
                sort_keys=True,
            )
            thresholds_path.write_text(
                threshold_content,
                encoding="utf-8",
            )

            with self.assertRaisesMessage(
                CommandError,
                "non-admissible evidence authority",
            ):
                call_command(
                    "admit_release_evidence",
                    bundle=bundle_path,
                    raw_root=root,
                    output=output_path,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=thresholds_path,
                    expected_thresholds_sha256=hashlib.sha256(
                        threshold_content.encode("utf-8")
                    ).hexdigest(),
                    max_age_seconds=86400,
                )

            self.assertFalse(output_path.exists())

    def test_result_timestamps_cannot_extend_past_bundle_generation(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            bundle["generated_at"] = (
                self.now - timedelta(hours=2)
            ).isoformat()

            with self.assertRaisesMessage(
                ReleaseEvidenceAdmissionError,
                "after bundle generation",
            ):
                validate_synthetic_release_evidence_fixture(
                    bundle=bundle,
                    raw_root=root,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=self._agreed_thresholds(),
                    now=self.now,
                    max_age_seconds=86400,
                )

    def test_hash_valid_raw_result_with_sensitive_content_is_rejected(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            manifest = next(
                entry
                for entry in bundle["raw_results"]
                if entry["scenario_id"] == "CANDIDATE-SMOKE"
            )
            content = (
                '{"scenario_id":"CANDIDATE-SMOKE",'
                '"access_token":"header.payload.signature"}\n'
            )
            (root / manifest["path"]).write_text(
                content,
                encoding="utf-8",
            )
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            manifest["sha256"] = digest
            manifest["byte_count"] = len(content.encode("utf-8"))
            bundle["candidate"]["raw_result_sha256"] = digest

            with self.assertRaisesMessage(
                ReleaseEvidenceAdmissionError,
                "sensitive evidence",
            ):
                validate_synthetic_release_evidence_fixture(
                    bundle=bundle,
                    raw_root=root,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=self._agreed_thresholds(),
                    now=self.now,
                    max_age_seconds=86400,
                )

    def test_dataset_load_and_tool_manifests_are_mandatory(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            invalid_cases = {}

            missing_counts = deepcopy(bundle)
            del missing_counts["dataset_load_manifest"]["counts"]
            invalid_cases["dataset-counts"] = missing_counts

            missing_load = deepcopy(bundle)
            del missing_load["dataset_load_manifest"]["load_profile"]
            invalid_cases["load-profile"] = missing_load

            missing_tool = deepcopy(bundle)
            del missing_tool["tool_versions"]["collector"]
            invalid_cases["collector-version"] = missing_tool

            for name, invalid in invalid_cases.items():
                with self.subTest(name=name):
                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        "manifest",
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=invalid,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_each_result_must_be_fresh_and_post_smoke(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            old = deepcopy(bundle)
            old_result = old["performance_results"][0]
            old_result["started_at"] = (
                self.now - timedelta(days=2, minutes=1)
            ).isoformat()
            old_result["ended_at"] = (
                self.now - timedelta(days=2)
            ).isoformat()

            with self.assertRaisesMessage(
                ReleaseEvidenceAdmissionError,
                "predates smoke",
            ):
                validate_synthetic_release_evidence_fixture(
                    bundle=old,
                    raw_root=root,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=self._agreed_thresholds(),
                    now=self.now,
                    max_age_seconds=86400,
                )

    def test_environment_threshold_is_evaluated_from_observations(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            environment_bound = next(
                result
                for result in bundle["performance_results"]
                if result["environment_threshold"] is not None
            )
            environment_bound["observed"]["p95"] = 2
            environment_bound["threshold_met"] = True

            with self.assertRaisesMessage(
                ReleaseEvidenceAdmissionError,
                "performance threshold failed",
            ):
                validate_synthetic_release_evidence_fixture(
                    bundle=bundle,
                    raw_root=root,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=self._agreed_thresholds(),
                    now=self.now,
                    max_age_seconds=86400,
                )

    def test_environment_threshold_must_match_the_agreed_manifest(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            environment_bound = next(
                result
                for result in bundle["performance_results"]
                if result["environment_threshold"] is not None
            )
            environment_bound["environment_threshold"]["value"] = 1000

            with self.assertRaisesMessage(
                ReleaseEvidenceAdmissionError,
                "agreed threshold mismatch",
            ):
                validate_synthetic_release_evidence_fixture(
                    bundle=bundle,
                    raw_root=root,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=self._agreed_thresholds(),
                    now=self.now,
                    max_age_seconds=86400,
                )

    def test_candidate_smoke_must_be_fresh(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            bundle["candidate"]["smoke_completed_at"] = (
                self.now - timedelta(days=2)
            ).isoformat()

            with self.assertRaisesMessage(
                ReleaseEvidenceAdmissionError,
                "stale candidate smoke",
            ):
                validate_synthetic_release_evidence_fixture(
                    bundle=bundle,
                    raw_root=root,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=self._agreed_thresholds(),
                    now=self.now,
                    max_age_seconds=86400,
                )

    def test_counts_and_measurements_are_enforced(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            invalid_cases = {}

            missing_observation = deepcopy(bundle)
            del missing_observation["performance_results"][0]["observed"][
                "sample_count"
            ]
            invalid_cases["performance"] = missing_observation

            missing_count = deepcopy(bundle)
            del missing_count["soak_results"][0]["counts"]["attempted"]
            invalid_cases["soak-count"] = missing_count

            missing_metric = deepcopy(bundle)
            missing_metric["soak_results"][0]["metrics"] = {}
            invalid_cases["soak-metric"] = missing_metric

            for name, invalid in invalid_cases.items():
                with self.subTest(name=name):
                    with self.assertRaisesMessage(
                        ReleaseEvidenceAdmissionError,
                        "measurement",
                    ):
                        validate_synthetic_release_evidence_fixture(
                            bundle=invalid,
                            raw_root=root,
                            expected_commit=self.candidate_commit,
                            expected_environment=self.environment_id,
                            agreed_thresholds=self._agreed_thresholds(),
                            now=self.now,
                            max_age_seconds=86400,
                        )

    def test_raw_json_must_match_the_admitted_summary(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle = self._bundle(root)
            bundle["performance_results"][0]["observed"]["p95"] *= 0.9

            with self.assertRaisesMessage(
                ReleaseEvidenceAdmissionError,
                "raw result content mismatch",
            ):
                validate_synthetic_release_evidence_fixture(
                    bundle=bundle,
                    raw_root=root,
                    expected_commit=self.candidate_commit,
                    expected_environment=self.environment_id,
                    agreed_thresholds=self._agreed_thresholds(),
                    now=self.now,
                    max_age_seconds=86400,
                )

    def _bundle(self, root):
        smoke_completed = self.now - timedelta(hours=5)
        raw_results = []

        def attach_raw(scenario_id, result):
            relative_path = Path("raw") / f"{scenario_id}.json"
            path = root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "scenario_id": scenario_id,
                "commit": self.candidate_commit,
                "environment_id": self.environment_id,
                "result": result,
            }
            content = json.dumps(
                payload,
                separators=(",", ":"),
                sort_keys=True,
            ) + "\n"
            path.write_text(content, encoding="utf-8")
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            raw_results.append(
                {
                    "scenario_id": scenario_id,
                    "path": relative_path.as_posix(),
                    "sha256": digest,
                    "byte_count": len(content.encode("utf-8")),
                }
            )
            return {**result, "raw_result_sha256": digest}

        candidate = attach_raw(
            "CANDIDATE-SMOKE",
            {
                "commit": self.candidate_commit,
                "environment_id": self.environment_id,
                "environment_class": "staging",
                "smoke_completed_at": smoke_completed.isoformat(),
                "smoke_result": "pass",
            },
        )
        performance_results = []
        soak_results = []
        for scenario in validate_scenario_matrix(PERFORMANCE_SCENARIOS):
            scenario_id = scenario["scenario_id"]
            if scenario_id in PROBE_IDS:
                duration = (
                    timedelta(hours=4)
                    if scenario_id == "PROBE-SUSTAINED-WORKFLOW"
                    else timedelta(minutes=10)
                )
                started_at = smoke_completed + timedelta(minutes=1)
                ended_at = started_at + duration
                soak_results.append(
                    attach_raw(
                        scenario_id,
                        {
                            "scenario_id": scenario_id,
                            "status": "pass",
                            "intervals": [
                                {
                                    "started_at": started_at.isoformat(),
                                    "ended_at": ended_at.isoformat(),
                                }
                            ],
                            "actual_elapsed_seconds": duration.total_seconds(),
                            "timing_source": "environment_monotonic_clock",
                            "threshold": scenario["threshold"],
                            "threshold_met": True,
                            "counts": {"attempted": 1, "failed": 0},
                            "metrics": {
                                "sample_count": 1,
                                "p95": 0.5,
                                "throughput": 1.0,
                            },
                            "outcome": self._probe_outcome(scenario_id),
                        },
                    )
                )
            else:
                threshold = scenario["threshold"]
                started_at = smoke_completed + timedelta(minutes=1)
                ended_at = started_at + timedelta(minutes=1)
                performance_results.append(
                    attach_raw(
                        scenario_id,
                        {
                            "scenario_id": scenario_id,
                            "status": "pass",
                            "started_at": started_at.isoformat(),
                            "ended_at": ended_at.isoformat(),
                            "actual_elapsed_seconds": 60,
                            "source_load": scenario["source_load"],
                            "measure": scenario["measure"],
                            "threshold": threshold,
                            "environment_threshold": (
                                None
                                if threshold["kind"] == "maximum_seconds"
                                else {
                                    "field": "p95",
                                    "comparison": "less_than_or_equal",
                                    "value": 1,
                                    "unit": "environment-defined",
                                }
                            ),
                            "threshold_met": True,
                            "observed": {
                                "sample_count": 3,
                                "p95": (
                                    threshold["value"] / 2
                                    if threshold["kind"] == "maximum_seconds"
                                    else 0.5
                                ),
                                "throughput": 1.0,
                                "processed_count": 10,
                            },
                        },
                    )
                )
        return {
            "schema_version": 1,
            "evidence_authority": "synthetic-parser-fixture",
            "synthetic": True,
            "generated_at": (self.now - timedelta(minutes=1)).isoformat(),
            "candidate": candidate,
            "dataset_load_manifest": {
                "dataset_id": "sanitised-capacity-fixture",
                "counts": {"members": 100, "documents": 1000},
                "load_profile": "test-plan-24.1-24.3",
            },
            "tool_versions": {
                "collector": "sfpcl-load-runner 1.0",
                "database": "postgresql",
                "worker": "celery",
                "redis": "redis",
            },
            "performance_results": performance_results,
            "soak_results": soak_results,
            "raw_results": raw_results,
        }

    @staticmethod
    def _agreed_thresholds():
        threshold = {
            "field": "p95",
            "comparison": "less_than_or_equal",
            "value": 1,
            "unit": "environment-defined",
        }
        return {
            scenario["scenario_id"]: threshold
            for scenario in validate_scenario_matrix(PERFORMANCE_SCENARIOS)
            if (
                scenario["scenario_id"] not in PROBE_IDS
                and scenario["threshold"]["kind"] == "environment_bound"
            )
        }

    @staticmethod
    def _probe_outcome(probe_id):
        digest = "c" * 64
        return {
            "PROBE-SUSTAINED-WORKFLOW": {
                "stable_memory": True,
                "stable_latency": True,
            },
            "PROBE-LARGE-DOCUMENT-VOLUME": {"storage_stable": True},
            "PROBE-LARGE-AUDIT-TABLE": {"queries_acceptable": True},
            "PROBE-HEAVY-EXPORT-QUEUE": {"api_responsive": True},
            "PROBE-WORKER-RESTART": {
                "idempotent_recovery": True,
                "duplicate_outputs": 0,
            },
            "PROBE-REDIS-RESTART": {
                "system_of_record_before_sha256": digest,
                "system_of_record_after_sha256": digest,
                "data_loss_count": 0,
            },
            "PROBE-DATABASE-PRESSURE": {
                "controlled_degradation": True,
                "recovered": True,
            },
        }[probe_id]
