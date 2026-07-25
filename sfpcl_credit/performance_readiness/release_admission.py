from collections import Counter
from copy import deepcopy
import hashlib
import json
from datetime import datetime
import math
import re

from sfpcl_credit.performance_readiness.matrix import (
    PERFORMANCE_SCENARIOS,
    PROBE_IDS,
    required_scenario_ids,
    validate_scenario_matrix,
)
from sfpcl_credit.performance_readiness.probes import validate_probe_outcome
from sfpcl_credit.performance_readiness.runner import (
    EvidenceValidationError,
)


class ReleaseEvidenceAdmissionError(ValueError):
    pass


def admit_release_evidence(
    *,
    bundle,
    raw_root,
    expected_commit,
    expected_environment,
    agreed_thresholds,
    now,
    max_age_seconds,
):
    return _validate_release_evidence(
        bundle=bundle,
        raw_root=raw_root,
        expected_commit=expected_commit,
        expected_environment=expected_environment,
        agreed_thresholds=agreed_thresholds,
        now=now,
        max_age_seconds=max_age_seconds,
        synthetic_fixture=False,
    )


def validate_synthetic_release_evidence_fixture(
    *,
    bundle,
    raw_root,
    expected_commit,
    expected_environment,
    agreed_thresholds,
    now,
    max_age_seconds,
):
    return _validate_release_evidence(
        bundle=bundle,
        raw_root=raw_root,
        expected_commit=expected_commit,
        expected_environment=expected_environment,
        agreed_thresholds=agreed_thresholds,
        now=now,
        max_age_seconds=max_age_seconds,
        synthetic_fixture=True,
    )


def _validate_release_evidence(
    *,
    bundle,
    raw_root,
    expected_commit,
    expected_environment,
    agreed_thresholds,
    now,
    max_age_seconds,
    synthetic_fixture,
):
    required_authority = (
        "synthetic-parser-fixture"
        if synthetic_fixture
        else "environment-release-evidence"
    )
    if (
        bundle.get("schema_version") != 1
        or bundle.get("evidence_authority") != required_authority
        or bundle.get("synthetic") is not synthetic_fixture
    ):
        raise ReleaseEvidenceAdmissionError(
            "non-admissible evidence authority"
        )
    _reject_sensitive_evidence(bundle)
    generated_at = _timestamp(
        bundle.get("generated_at"),
        label="bundle",
    )
    age_seconds = (now - generated_at).total_seconds()
    if (
        not isinstance(max_age_seconds, int)
        or isinstance(max_age_seconds, bool)
        or max_age_seconds <= 0
        or age_seconds < 0
        or age_seconds > max_age_seconds
    ):
        raise ReleaseEvidenceAdmissionError("stale release evidence")
    candidate = bundle.get("candidate")
    if not isinstance(candidate, dict):
        raise ReleaseEvidenceAdmissionError("missing candidate identity")
    if candidate.get("commit") != expected_commit:
        raise ReleaseEvidenceAdmissionError("candidate commit mismatch")
    if candidate.get("environment_id") != expected_environment:
        raise ReleaseEvidenceAdmissionError("environment mismatch")
    if (
        candidate.get("environment_class") != "staging"
        or candidate.get("smoke_result") != "pass"
    ):
        raise ReleaseEvidenceAdmissionError(
            "candidate smoke/environment is not release admissible"
        )
    _validate_manifests(bundle)
    identifiers = [
        result.get("scenario_id")
        for result in bundle.get("soak_results", [])
    ]
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    if duplicates:
        raise ReleaseEvidenceAdmissionError(
            f"duplicate soak results: {duplicates}"
        )
    missing = sorted(set(PROBE_IDS) - set(identifiers))
    if missing:
        raise ReleaseEvidenceAdmissionError(
            f"missing soak results: {missing}"
        )
    unknown = sorted(set(identifiers) - set(PROBE_IDS))
    if unknown:
        raise ReleaseEvidenceAdmissionError(
            f"unknown soak results: {unknown}"
        )
    smoke_completed_at = _timestamp(
        candidate.get("smoke_completed_at"),
        label="candidate smoke",
    )
    smoke_age_seconds = (now - smoke_completed_at).total_seconds()
    if (
        smoke_age_seconds < 0
        or smoke_age_seconds > max_age_seconds
    ):
        raise ReleaseEvidenceAdmissionError("stale candidate smoke")
    for result in bundle["soak_results"]:
        scenario_id = result["scenario_id"]
        scenario = next(
            item
            for item in PERFORMANCE_SCENARIOS
            if item["scenario_id"] == scenario_id
        )
        if (
            result.get("status") != "pass"
            or result.get("threshold_met") is not True
            or result.get("threshold") != scenario["threshold"]
        ):
            raise ReleaseEvidenceAdmissionError(
                f"{scenario_id}: soak threshold/result failed"
            )
        try:
            validate_probe_outcome(
                scenario_id,
                result.get("outcome"),
            )
        except EvidenceValidationError as error:
            raise ReleaseEvidenceAdmissionError(str(error)) from error
        _validate_elapsed_time(
            result,
            smoke_completed_at=smoke_completed_at,
            generated_at=generated_at,
            now=now,
            max_age_seconds=max_age_seconds,
        )
        _validate_soak_measurements(result)
    _validate_performance_results(
        bundle.get("performance_results"),
        smoke_completed_at=smoke_completed_at,
        generated_at=generated_at,
        now=now,
        max_age_seconds=max_age_seconds,
        agreed_thresholds=agreed_thresholds,
    )
    _validate_raw_results(
        bundle=bundle,
        raw_root=raw_root,
    )
    summary = {
        "schema_version": 1,
        "result": (
            "synthetic-validation-pass"
            if synthetic_fixture
            else "admitted"
        ),
        "release_ready": not synthetic_fixture,
        "commit": expected_commit,
        "environment_id": expected_environment,
        "generated_at": bundle["generated_at"],
        "candidate": deepcopy(bundle["candidate"]),
        "dataset_load_manifest": deepcopy(
            bundle["dataset_load_manifest"]
        ),
        "tool_versions": deepcopy(bundle["tool_versions"]),
        "performance_results": deepcopy(bundle["performance_results"]),
        "soak_results": deepcopy(bundle["soak_results"]),
        "raw_results": deepcopy(bundle["raw_results"]),
        "counts": {
            "performance_results": len(
                bundle.get("performance_results", [])
            ),
            "soak_results": len(identifiers),
        },
    }
    canonical = json.dumps(
        summary,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    summary["summary_sha256"] = hashlib.sha256(canonical).hexdigest()
    return summary


def _validate_elapsed_time(
    result,
    *,
    smoke_completed_at,
    generated_at,
    now,
    max_age_seconds,
):
    scenario_id = result["scenario_id"]
    if result.get("timing_source") != "environment_monotonic_clock":
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: untrusted timing source"
        )
    intervals = result.get("intervals")
    if not isinstance(intervals, list) or not intervals:
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: missing timing intervals"
        )
    elapsed_seconds = 0
    previous_end = None
    for interval in intervals:
        if not isinstance(interval, dict):
            raise ReleaseEvidenceAdmissionError(
                f"{scenario_id}: malformed timing interval"
            )
        started_at = _timestamp(
            interval.get("started_at"),
            label=scenario_id,
        )
        ended_at = _timestamp(
            interval.get("ended_at"),
            label=scenario_id,
        )
        if started_at < smoke_completed_at:
            raise ReleaseEvidenceAdmissionError(
                f"{scenario_id}: result predates deployment smoke"
            )
        if ended_at <= started_at:
            raise ReleaseEvidenceAdmissionError(
                f"{scenario_id}: clock reversal"
            )
        if ended_at > generated_at:
            raise ReleaseEvidenceAdmissionError(
                f"{scenario_id}: result ends after bundle generation"
            )
        age_seconds = (now - ended_at).total_seconds()
        if age_seconds < 0 or age_seconds > max_age_seconds:
            raise ReleaseEvidenceAdmissionError(
                f"{scenario_id}: stale scenario evidence"
            )
        if previous_end is not None and started_at < previous_end:
            raise ReleaseEvidenceAdmissionError(
                f"{scenario_id}: overlapping timing intervals"
            )
        elapsed_seconds += (ended_at - started_at).total_seconds()
        previous_end = ended_at
    supplied_elapsed = result.get("actual_elapsed_seconds")
    if (
        not isinstance(supplied_elapsed, (int, float))
        or isinstance(supplied_elapsed, bool)
        or supplied_elapsed != elapsed_seconds
    ):
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: elapsed duration mismatch"
        )
    if (
        scenario_id == "PROBE-SUSTAINED-WORKFLOW"
        and elapsed_seconds < 4 * 60 * 60
    ):
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: four-hour duration shortfall"
        )


def _validate_soak_measurements(result):
    scenario_id = result["scenario_id"]
    counts = result.get("counts")
    metrics = result.get("metrics")
    if (
        not isinstance(counts, dict)
        or not _positive_integer(counts.get("attempted"))
        or counts.get("failed") != 0
        or not _valid_observations(metrics, require_processed=False)
    ):
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: invalid soak measurements"
        )


def _validate_manifests(bundle):
    dataset = bundle.get("dataset_load_manifest")
    if not isinstance(dataset, dict):
        raise ReleaseEvidenceAdmissionError(
            "missing dataset/load manifest"
        )
    if not all(
        dataset.get(field)
        for field in ("dataset_id", "counts", "load_profile")
    ):
        raise ReleaseEvidenceAdmissionError(
            "incomplete dataset/load manifest"
        )
    counts = dataset["counts"]
    if (
        not isinstance(counts, dict)
        or not counts
        or any(
            not isinstance(count, int)
            or isinstance(count, bool)
            or count < 0
            for count in counts.values()
        )
    ):
        raise ReleaseEvidenceAdmissionError(
            "invalid dataset/load manifest counts"
        )
    tools = bundle.get("tool_versions")
    required_tools = {"collector", "database", "worker", "redis"}
    if (
        not isinstance(tools, dict)
        or any(
            not isinstance(tools.get(tool), str)
            or not tools[tool].strip()
            for tool in required_tools
        )
    ):
        raise ReleaseEvidenceAdmissionError(
            "incomplete tool version manifest"
        )


def _validate_performance_results(
    results,
    *,
    smoke_completed_at,
    generated_at,
    now,
    max_age_seconds,
    agreed_thresholds,
):
    if not isinstance(results, list):
        raise ReleaseEvidenceAdmissionError(
            "missing performance results"
        )
    scenarios = {
        scenario["scenario_id"]: scenario
        for scenario in validate_scenario_matrix(PERFORMANCE_SCENARIOS)
        if scenario["scenario_id"] not in PROBE_IDS
    }
    environment_bound_ids = {
        scenario_id
        for scenario_id, scenario in scenarios.items()
        if scenario["threshold"]["kind"] == "environment_bound"
    }
    if (
        not isinstance(agreed_thresholds, dict)
        or set(agreed_thresholds) != environment_bound_ids
    ):
        raise ReleaseEvidenceAdmissionError(
            "agreed threshold manifest mismatch"
        )
    identifiers = [result.get("scenario_id") for result in results]
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    missing = sorted(set(scenarios) - set(identifiers))
    unknown = sorted(set(identifiers) - set(scenarios))
    if duplicates:
        raise ReleaseEvidenceAdmissionError(
            f"duplicate performance results: {duplicates}"
        )
    if missing:
        raise ReleaseEvidenceAdmissionError(
            f"missing performance results: {missing}"
        )
    if unknown:
        raise ReleaseEvidenceAdmissionError(
            f"unknown performance results: {unknown}"
        )
    for result in results:
        scenario = scenarios[result["scenario_id"]]
        _validate_performance_window(
            result,
            smoke_completed_at=smoke_completed_at,
            generated_at=generated_at,
            now=now,
            max_age_seconds=max_age_seconds,
        )
        if (
            result.get("status") != "pass"
            or result.get("threshold_met") is not True
        ):
            raise ReleaseEvidenceAdmissionError(
                f"performance threshold failed: {result['scenario_id']}"
            )
        for field in ("source_load", "measure", "threshold"):
            if result.get(field) != scenario[field]:
                raise ReleaseEvidenceAdmissionError(
                    "performance contract mismatch: "
                    f"{result['scenario_id']} {field}"
                )
        threshold = scenario["threshold"]
        observed = result.get("observed")
        if not _valid_observations(observed, require_processed=True):
            raise ReleaseEvidenceAdmissionError(
                f"performance measurements missing: {result['scenario_id']}"
            )
        if threshold["kind"] == "maximum_seconds":
            p95 = observed.get("p95")
            if (
                not isinstance(p95, (int, float))
                or isinstance(p95, bool)
                or p95 >= threshold["value"]
            ):
                raise ReleaseEvidenceAdmissionError(
                    "performance threshold failed: "
                    f"{result['scenario_id']}"
                )
        else:
            environment_threshold = result.get("environment_threshold")
            if (
                environment_threshold
                != agreed_thresholds[result["scenario_id"]]
            ):
                raise ReleaseEvidenceAdmissionError(
                    "agreed threshold mismatch: "
                    f"{result['scenario_id']}"
                )
            if not _environment_threshold_passes(
                environment_threshold,
                observed,
            ):
                raise ReleaseEvidenceAdmissionError(
                    "performance threshold failed: "
                    f"{result['scenario_id']}"
                )


def _validate_performance_window(
    result,
    *,
    smoke_completed_at,
    generated_at,
    now,
    max_age_seconds,
):
    scenario_id = result["scenario_id"]
    started_at = _timestamp(result.get("started_at"), label=scenario_id)
    ended_at = _timestamp(result.get("ended_at"), label=scenario_id)
    if started_at < smoke_completed_at or ended_at <= started_at:
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: performance result predates smoke"
        )
    if ended_at > generated_at:
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: result ends after bundle generation"
        )
    age_seconds = (now - ended_at).total_seconds()
    if age_seconds < 0 or age_seconds > max_age_seconds:
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: stale scenario evidence"
        )
    elapsed_seconds = (ended_at - started_at).total_seconds()
    if result.get("actual_elapsed_seconds") != elapsed_seconds:
        raise ReleaseEvidenceAdmissionError(
            f"{scenario_id}: elapsed duration mismatch"
        )


def _valid_observations(observed, *, require_processed):
    if not isinstance(observed, dict):
        return False
    if not _positive_integer(observed.get("sample_count")):
        return False
    if require_processed and not _nonnegative_integer(
        observed.get("processed_count")
    ):
        return False
    return all(
        _nonnegative_number(observed.get(field))
        for field in ("p95", "throughput")
    )


def _environment_threshold_passes(threshold, observed):
    if not isinstance(threshold, dict):
        return False
    if set(threshold) != {"field", "comparison", "value", "unit"}:
        return False
    field = threshold["field"]
    comparison = threshold["comparison"]
    expected = threshold["value"]
    actual = observed.get(field)
    if (
        not isinstance(field, str)
        or not isinstance(threshold["unit"], str)
        or not threshold["unit"].strip()
        or not _nonnegative_number(actual)
        or not _nonnegative_number(expected)
    ):
        return False
    comparisons = {
        "less_than": lambda: actual < expected,
        "less_than_or_equal": lambda: actual <= expected,
        "greater_than_or_equal": lambda: actual >= expected,
        "equal": lambda: actual == expected,
    }
    evaluator = comparisons.get(comparison)
    return evaluator is not None and evaluator()


def _positive_integer(value):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value > 0
    )


def _nonnegative_integer(value):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def _nonnegative_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def _validate_raw_results(*, bundle, raw_root):
    manifest = bundle.get("raw_results")
    if not isinstance(manifest, list):
        raise ReleaseEvidenceAdmissionError("missing raw result manifest")
    expected_ids = {"CANDIDATE-SMOKE", *required_scenario_ids()}
    identifiers = [entry.get("scenario_id") for entry in manifest]
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    missing = sorted(expected_ids - set(identifiers))
    unknown = sorted(set(identifiers) - expected_ids)
    if duplicates:
        raise ReleaseEvidenceAdmissionError(
            f"duplicate raw results: {duplicates}"
        )
    if missing:
        raise ReleaseEvidenceAdmissionError(
            f"missing raw results: {missing}"
        )
    if unknown:
        raise ReleaseEvidenceAdmissionError(
            f"unknown raw results: {unknown}"
        )
    root = raw_root.resolve()
    hash_by_id = {}
    payload_by_id = {}
    for entry in manifest:
        relative = entry.get("path")
        if not isinstance(relative, str):
            raise ReleaseEvidenceAdmissionError("unsafe raw result path")
        path = root / relative
        try:
            resolved = path.resolve(strict=True)
        except OSError as error:
            raise ReleaseEvidenceAdmissionError(
                f"missing raw result file: {entry['scenario_id']}"
            ) from error
        if (
            not resolved.is_relative_to(root)
            or path.is_symlink()
            or not resolved.is_file()
        ):
            raise ReleaseEvidenceAdmissionError("unsafe raw result path")
        content = resolved.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if (
            entry.get("sha256") != digest
            or entry.get("byte_count") != len(content)
        ):
            raise ReleaseEvidenceAdmissionError(
                f"raw result hash mismatch: {entry['scenario_id']}"
            )
        try:
            raw_payload = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ReleaseEvidenceAdmissionError(
                f"invalid raw result JSON: {entry['scenario_id']}"
            ) from error
        _reject_sensitive_evidence(raw_payload)
        hash_by_id[entry["scenario_id"]] = digest
        payload_by_id[entry["scenario_id"]] = raw_payload
    evidence_rows = [
        bundle["candidate"],
        *bundle["performance_results"],
        *bundle["soak_results"],
    ]
    evidence_ids = [
        "CANDIDATE-SMOKE",
        *(
            result["scenario_id"]
            for result in bundle["performance_results"]
        ),
        *(result["scenario_id"] for result in bundle["soak_results"]),
    ]
    for scenario_id, result in zip(evidence_ids, evidence_rows, strict=True):
        if result.get("raw_result_sha256") != hash_by_id[scenario_id]:
            raise ReleaseEvidenceAdmissionError(
                f"raw result reference mismatch: {scenario_id}"
            )
        expected_result = {
            key: value
            for key, value in result.items()
            if key != "raw_result_sha256"
        }
        if payload_by_id[scenario_id] != {
            "scenario_id": scenario_id,
            "commit": bundle["candidate"]["commit"],
            "environment_id": bundle["candidate"]["environment_id"],
            "result": expected_result,
        }:
            raise ReleaseEvidenceAdmissionError(
                f"raw result content mismatch: {scenario_id}"
            )


def _timestamp(value, *, label):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise ReleaseEvidenceAdmissionError(
            f"{label}: malformed timestamp"
        ) from error
    if parsed.utcoffset() is None:
        raise ReleaseEvidenceAdmissionError(
            f"{label}: timestamp must include timezone"
        )
    return parsed


_SENSITIVE_KEY_PARTS = (
    "password",
    "token",
    "credential",
    "secret",
    "api_key",
    "otp",
)
_EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])"
)
_PAN_PATTERN = re.compile(r"(?<![A-Z0-9])[A-Z]{5}[0-9]{4}[A-Z](?![A-Z0-9])")
_AADHAAR_PATTERN = re.compile(r"(?<!\d)\d{12}(?!\d)")


def _reject_sensitive_evidence(value, *, field_name=None):
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).lower()
            if any(part in normalized for part in _SENSITIVE_KEY_PARTS):
                raise ReleaseEvidenceAdmissionError(
                    "sensitive evidence field rejected"
                )
            _reject_sensitive_evidence(
                nested,
                field_name=normalized,
            )
    elif isinstance(value, list):
        for nested in value:
            _reject_sensitive_evidence(
                nested,
                field_name=field_name,
            )
    elif isinstance(value, str):
        if field_name in {
            "commit",
            "sha256",
            "raw_result_sha256",
            "system_of_record_before_sha256",
            "system_of_record_after_sha256",
        }:
            return
        if (
            "://" in value
            or _EMAIL_PATTERN.search(value)
            or _PAN_PATTERN.search(value)
            or _AADHAAR_PATTERN.search(value)
        ):
            raise ReleaseEvidenceAdmissionError(
                "sensitive evidence value rejected"
            )
