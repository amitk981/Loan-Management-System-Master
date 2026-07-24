from collections import Counter
import hashlib
import json
import math
from datetime import datetime, timezone

from sfpcl_credit.performance_readiness.matrix import (
    PERFORMANCE_SCENARIOS,
    required_scenario_ids,
    validate_scenario_matrix,
)


class EvidenceValidationError(ValueError):
    pass


def build_performance_summary(
    *,
    scenario_results,
    environment,
    expected_commit,
    now=None,
    max_age_seconds=None,
):
    matrix = validate_scenario_matrix(PERFORMANCE_SCENARIOS)
    required_environment_fields = {
        "environment_id",
        "environment_class",
        "commit",
        "generated_at",
        "seed",
        "dataset_counts",
        "tool_versions",
    }
    allowed_environment_fields = {
        *required_environment_fields,
        "operating_system",
        "cpu_count",
        "database_engine",
        "database_version",
        "redis_version",
        "worker_version",
        "frontend_version",
    }
    missing_environment = sorted(
        required_environment_fields - set(environment)
    )
    if missing_environment:
        raise EvidenceValidationError(
            f"missing environment facts: {missing_environment}"
        )
    unknown_environment = sorted(
        set(environment) - allowed_environment_fields
    )
    if unknown_environment:
        raise EvidenceValidationError(
            f"unsafe environment facts: {unknown_environment}"
        )
    if environment["commit"] != expected_commit:
        raise EvidenceValidationError("commit mismatch")
    if max_age_seconds is not None:
        try:
            generated_at = datetime.fromisoformat(
                environment["generated_at"].replace("Z", "+00:00")
            )
        except (AttributeError, TypeError, ValueError) as error:
            raise EvidenceValidationError("malformed generated_at") from error
        reference_time = now or datetime.now(timezone.utc)
        age_seconds = (reference_time - generated_at).total_seconds()
        if age_seconds < 0 or age_seconds > max_age_seconds:
            raise EvidenceValidationError("stale evidence")
    identifiers = [result.get("scenario_id") for result in scenario_results]
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    if duplicates:
        raise EvidenceValidationError(f"duplicate results: {duplicates}")
    missing = sorted(required_scenario_ids() - set(identifiers))
    if missing:
        raise EvidenceValidationError(f"missing results: {missing}")
    unknown = sorted(set(identifiers) - required_scenario_ids())
    if unknown:
        raise EvidenceValidationError(f"unknown results: {unknown}")

    result_by_id = {
        result["scenario_id"]: result for result in scenario_results
    }
    evaluated = [
        _evaluate_scenario(scenario, result_by_id[scenario["scenario_id"]])
        for scenario in matrix
    ]
    failing_scenarios = [
        result["scenario_id"]
        for result in evaluated
        if result["status"] == "fail"
    ]
    summary = {
        "schema_version": 1,
        "result": "fail" if failing_scenarios else "bounded-local-pass",
        "release_ready": False,
        "release_readiness_reason": "012F3_RELEASE_EVIDENCE_REQUIRED",
        "commit": expected_commit,
        "environment": environment,
        "counts": {
            status: sum(result["status"] == status for result in evaluated)
            for status in ("pass", "fail", "release-evidence-required")
        },
        "failing_scenarios": failing_scenarios,
        "approved_skips": [],
        "scenarios": evaluated,
    }
    canonical = json.dumps(
        summary,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    summary["summary_sha256"] = hashlib.sha256(canonical).hexdigest()
    return summary


def _evaluate_scenario(scenario, raw_result):
    supplied_status = raw_result.get("status")
    if supplied_status not in {
        "pass",
        "fail",
        "release-evidence-required",
    }:
        raise EvidenceValidationError(
            f"unsupported status: {scenario['scenario_id']}"
        )
    samples = raw_result.get("samples")
    if (
        not isinstance(samples, list)
        or not samples
        or any(
            not isinstance(sample, (int, float))
            or isinstance(sample, bool)
            or not math.isfinite(sample)
            or sample < 0
            for sample in samples
        )
    ):
        raise EvidenceValidationError(
            f"malformed samples: {scenario['scenario_id']}"
        )
    digest = raw_result.get("raw_result_sha256", "")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise EvidenceValidationError(
            f"malformed raw result hash: {scenario['scenario_id']}"
        )
    canonical_raw_result = json.dumps(
        {
            "samples": samples,
            "status": supplied_status,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if hashlib.sha256(canonical_raw_result).hexdigest() != digest:
        raise EvidenceValidationError(
            f"raw result hash mismatch: {scenario['scenario_id']}"
        )

    warm_up_count = scenario["warm_up_repetitions"]
    cold_samples = samples[:warm_up_count]
    measured_samples = samples[warm_up_count:] or samples
    ordered = sorted(measured_samples)
    p95 = ordered[math.ceil(0.95 * len(ordered)) - 1]
    threshold = scenario["threshold"]
    if supplied_status == "fail":
        status = "fail"
    elif threshold["kind"] == "maximum_seconds":
        if supplied_status != "pass":
            raise EvidenceValidationError(
                f"unsupported status: {scenario['scenario_id']}"
            )
        status = "pass" if p95 < threshold["value"] else "fail"
    else:
        if supplied_status != "release-evidence-required":
            raise EvidenceValidationError(
                f"unsupported status: {scenario['scenario_id']}"
            )
        status = "release-evidence-required"
    return {
        **scenario,
        "status": status,
        "observed": {
            "bounded_local_measure": "public_behavior_duration_seconds",
            "declared_measure": scenario["measure"],
            "declared_measure_evaluated": (
                threshold["kind"] == "maximum_seconds"
            ),
            "executed_load": scenario["bounded_local_load"],
            "count": len(measured_samples),
            "minimum": ordered[0],
            "maximum": ordered[-1],
            "p50": ordered[math.ceil(0.50 * len(ordered)) - 1],
            "p95": p95,
            "cold_samples": cold_samples,
            "warm_samples": measured_samples,
        },
        "raw_result_sha256": digest,
    }
