from collections import Counter


class MatrixValidationError(ValueError):
    pass


PERF_IDS = tuple(f"PERF-{number:03d}" for number in range(1, 11))
TARGET_IDS = (
    "TARGET-LOGIN",
    "TARGET-DASHBOARD",
    "TARGET-MEMBER-SEARCH",
    "TARGET-APPLICATION-DETAIL",
    "TARGET-LOAN-ACCOUNT-360",
    "TARGET-APPROVAL-ACTION",
    "TARGET-DISBURSEMENT-READINESS",
    "TARGET-DOCUMENT-UPLOAD",
    "TARGET-REPORT-EXPORT",
    "TARGET-DPD-BATCH",
    "TARGET-MONTHLY-ACCRUAL",
    "TARGET-CAPITALISATION-DRY-RUN",
)
PROBE_IDS = (
    "PROBE-SUSTAINED-WORKFLOW",
    "PROBE-LARGE-DOCUMENT-VOLUME",
    "PROBE-LARGE-AUDIT-TABLE",
    "PROBE-HEAVY-EXPORT-QUEUE",
    "PROBE-WORKER-RESTART",
    "PROBE-REDIS-RESTART",
    "PROBE-DATABASE-PRESSURE",
)


def required_scenario_ids():
    return {*PERF_IDS, *TARGET_IDS, *PROBE_IDS}


def _fixed(seconds):
    return {
        "kind": "maximum_seconds",
        "value": seconds,
        "comparison": "less_than",
    }


def _environment_bound(requirement):
    return {
        "kind": "environment_bound",
        "value": None,
        "comparison": requirement,
    }


def _scenario(
    scenario_id,
    *,
    scenario,
    seam,
    role,
    dataset,
    source_load,
    local_load,
    measure,
    threshold,
    source,
    authority="bounded-local",
    warm_up=1,
    repetitions=3,
):
    return {
        "scenario_id": scenario_id,
        "scenario": scenario,
        "public_seam": seam,
        "least_privilege_role": role,
        "dataset_size": dataset,
        "source_load": source_load,
        "bounded_local_load": local_load,
        "warm_up_repetitions": warm_up,
        "measured_repetitions": repetitions,
        "measure": measure,
        "threshold": threshold,
        "threshold_source": source,
        "authority": authority,
    }


_TEST_PLAN = "docs/source/test-plan.md §24"
_OPS = "docs/source/deployment-ops.md §32.4"
_LOCAL_SINGLE = {"concurrency": 1, "iterations": 3}
_ACTIVE_LOANS = {"dataset": "full_active_loan_test_set"}

PERFORMANCE_SCENARIOS = (
    _scenario(
        "PERF-001", scenario="Concurrent login",
        seam="POST /api/v1/auth/login/", role="active_staff",
        dataset="100 synthetic staff accounts", source_load={"users": [50, 100]},
        local_load={"users": 2}, measure="latency_p95_seconds",
        threshold=_fixed(2), source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-002", scenario="Dashboard load",
        seam="GET /api/v1/dashboard/", role="credit_manager",
        dataset="role-scoped populated dashboard", source_load={"users": 50},
        local_load={"users": 2}, measure="latency_p95_seconds",
        threshold=_fixed(3), source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-003", scenario="Member search",
        seam="GET /api/v1/members/?search=<synthetic>", role="field_officer",
        dataset="paginated synthetic member directory", source_load={"users": 25},
        local_load={"users": 2}, measure="latency_p95_seconds",
        threshold=_fixed(4), source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-004", scenario="Application creation",
        seam="POST /api/v1/loan-applications/", role="field_officer",
        dataset="20 isolated synthetic member drafts", source_load={"users": 20},
        local_load={"users": 1}, measure="throughput_per_second",
        threshold=_environment_bound("agreed_target_required"),
        source=f"{_TEST_PLAN}.2",
    ),
    _scenario(
        "PERF-005", scenario="Document upload",
        seam="POST /api/v1/documents/", role="field_officer",
        dataset="10 safe synthetic files with declared byte sizes",
        source_load={"concurrent_uploads": 10}, local_load={"concurrent_uploads": 1},
        measure="completion_seconds_and_progress_events",
        threshold=_environment_bound("agreed_file_size_target_required"),
        source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-006", scenario="Approval actions",
        seam="POST /api/v1/approval-cases/{id}/actions/", role="assigned_approver",
        dataset="10 independent scoped approval cases", source_load={"approvers": 10},
        local_load={"approvers": 1}, measure="latency_p95_seconds",
        threshold=_fixed(2), source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-007", scenario="Report export",
        seam="POST /api/v1/reports/exports/", role="report_exporter",
        dataset="5 heavy masked synthetic reports", source_load={"exports": 5},
        local_load={"exports": 1}, measure="enqueue_latency_and_completion_seconds",
        threshold=_environment_bound("asynchronous_when_completion_exceeds_5_seconds"),
        source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-008", scenario="DPD batch",
        seam="DPD calculation service public batch entrypoint", role="credit_manager",
        dataset="full active-loan test set", source_load=_ACTIVE_LOANS,
        local_load={"active_loans": 10}, measure="batch_duration_seconds",
        threshold=_environment_bound("agreed_batch_window_required"),
        source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-009", scenario="Interest accrual",
        seam="monthly accrual service public batch entrypoint", role="accounts",
        dataset="full active-loan test set", source_load=_ACTIVE_LOANS,
        local_load={"active_loans": 10}, measure="batch_duration_seconds",
        threshold=_environment_bound("agreed_batch_window_required"),
        source=f"{_TEST_PLAN}.1-.2",
    ),
    _scenario(
        "PERF-010", scenario="Audit log query",
        seam="GET /api/v1/audit/logs/", role="auditor",
        dataset="large sanitised synthetic audit set", source_load={"dataset": "large"},
        local_load={"audit_events": 100}, measure="latency_p95_seconds",
        threshold=_environment_bound("acceptable_query_target_required"),
        source=f"{_TEST_PLAN}.2",
    ),
    *(
        _scenario(
            scenario_id,
            scenario=scenario,
            seam=seam,
            role=role,
            dataset=dataset,
            source_load={"users": 1},
            local_load=_LOCAL_SINGLE,
            measure=measure,
            threshold=threshold,
            source=f"{_TEST_PLAN}.1; {_OPS}",
        )
        for scenario_id, scenario, seam, role, dataset, measure, threshold in (
            ("TARGET-LOGIN", "Login target", "POST /api/v1/auth/login/", "active_staff", "synthetic staff", "latency_p95_seconds", _fixed(2)),
            ("TARGET-DASHBOARD", "Dashboard target", "GET /api/v1/dashboard/", "credit_manager", "populated role dashboard", "latency_p95_seconds", _fixed(3)),
            ("TARGET-MEMBER-SEARCH", "Member search target", "GET /api/v1/members/?search=<synthetic>", "field_officer", "paginated members", "latency_p95_seconds", _fixed(4)),
            ("TARGET-APPLICATION-DETAIL", "Application Detail target", "GET /api/v1/loan-applications/{id}/", "credit_manager", "scoped application", "latency_p95_seconds", _fixed(3)),
            ("TARGET-LOAN-ACCOUNT-360", "Loan Account 360 target", "GET /api/v1/loan-accounts/{id}/", "credit_manager", "active scoped account", "latency_p95_seconds", _fixed(3)),
            ("TARGET-APPROVAL-ACTION", "Approval action target", "POST /api/v1/approval-cases/{id}/actions/", "assigned_approver", "independent approval case", "latency_p95_seconds", _fixed(2)),
            ("TARGET-DISBURSEMENT-READINESS", "Disbursement Readiness target", "GET /api/v1/loan-accounts/{id}/disbursement-readiness/", "senior_manager_finance", "ready scoped account", "latency_p95_seconds", _fixed(3)),
            ("TARGET-DOCUMENT-UPLOAD", "Document upload target", "POST /api/v1/documents/", "field_officer", "declared safe file size", "completion_seconds_and_progress_events", _environment_bound("agreed_file_size_target_required")),
            ("TARGET-REPORT-EXPORT", "Report export target", "POST /api/v1/reports/exports/", "report_exporter", "heavy masked report", "enqueue_latency_and_completion_seconds", _environment_bound("asynchronous_when_completion_exceeds_5_seconds")),
            ("TARGET-DPD-BATCH", "DPD batch target", "DPD calculation service public batch entrypoint", "credit_manager", "full active-loan test set", "batch_duration_seconds", _environment_bound("agreed_batch_window_required")),
            ("TARGET-MONTHLY-ACCRUAL", "Monthly accrual target", "monthly accrual service public batch entrypoint", "accounts", "full active-loan test set", "batch_duration_seconds", _environment_bound("agreed_batch_window_required")),
            ("TARGET-CAPITALISATION-DRY-RUN", "Capitalisation Dry Run target", "capitalisation dry-run service public entrypoint", "accounts", "eligible interest invoice set", "batch_duration_seconds", _environment_bound("agreed_batch_window_required")),
        )
    ),
    *(
        _scenario(
            scenario_id,
            scenario=scenario,
            seam=seam,
            role="operations_test_operator",
            dataset=dataset,
            source_load={"environment_run": requirement},
            local_load={"definition_probe": 1},
            warm_up=0,
            repetitions=1,
            measure=measure,
            threshold=_environment_bound(expected),
            source=f"{_TEST_PLAN}.3",
            authority="release-evidence-required",
        )
        for scenario_id, scenario, seam, dataset, requirement, measure, expected in (
            ("PROBE-SUSTAINED-WORKFLOW", "4-hour sustained workflow usage", "deployed public workflow/API paths", "isolated environment fixture", "4 real hours", "memory_and_latency_stability", "stable_memory_and_latency"),
            ("PROBE-LARGE-DOCUMENT-VOLUME", "Large document volume", "document upload/download public APIs", "large safe synthetic document set", "environment capacity", "storage_errors_latency_and_capacity", "storage_stable"),
            ("PROBE-LARGE-AUDIT-TABLE", "Large audit table", "GET /api/v1/audit/logs/", "large sanitised audit set", "environment capacity", "query_percentiles", "queries_acceptable"),
            ("PROBE-HEAVY-EXPORT-QUEUE", "Heavy export queue", "report export public API and reports worker", "heavy masked export set", "environment capacity", "api_latency_queue_depth_and_completion", "api_remains_responsive"),
            ("PROBE-WORKER-RESTART", "Worker restart during task", "public async job seam and worker operation", "one idempotent isolated job", "restart while running", "attempts_outputs_and_duplicate_count", "idempotent_recovery"),
            ("PROBE-REDIS-RESTART", "Redis restart", "public async job seam and Redis operation", "isolated persisted system-of-record snapshot", "restart while queued", "before_after_system_of_record_hash", "no_system_of_record_data_loss"),
            ("PROBE-DATABASE-PRESSURE", "Database connection pressure", "public API plus database monitoring", "isolated scoped workflow fixture", "connection pressure", "errors_latency_connections_and_recovery", "controlled_degradation"),
        )
    ),
)


def validate_scenario_matrix(matrix):
    required = required_scenario_ids()
    identifiers = [scenario.get("scenario_id") for scenario in matrix]
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    if duplicates:
        raise MatrixValidationError(f"duplicate scenarios: {duplicates}")
    missing = sorted(required - set(identifiers))
    if missing:
        raise MatrixValidationError(f"missing scenarios: {missing}")
    unknown = sorted(set(identifiers) - required)
    if unknown:
        raise MatrixValidationError(f"unknown scenarios: {unknown}")
    required_fields = {
        "scenario",
        "public_seam",
        "least_privilege_role",
        "dataset_size",
        "source_load",
        "bounded_local_load",
        "warm_up_repetitions",
        "measured_repetitions",
        "measure",
        "threshold",
        "threshold_source",
        "authority",
    }
    incomplete = sorted(
        scenario["scenario_id"]
        for scenario in matrix
        if required_fields - set(scenario)
    )
    if incomplete:
        raise MatrixValidationError(f"incomplete scenarios: {incomplete}")
    malformed_thresholds = sorted(
        scenario["scenario_id"]
        for scenario in matrix
        if not _valid_threshold(scenario["threshold"])
    )
    if malformed_thresholds:
        raise MatrixValidationError(
            f"malformed thresholds: {malformed_thresholds}"
        )
    return tuple(sorted(matrix, key=lambda scenario: scenario["scenario_id"]))


def _valid_threshold(threshold):
    if not isinstance(threshold, dict):
        return False
    kind = threshold.get("kind")
    if kind == "maximum_seconds":
        value = threshold.get("value")
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value > 0
            and threshold.get("comparison") == "less_than"
        )
    if kind == "environment_bound":
        return (
            threshold.get("value") is None
            and isinstance(threshold.get("comparison"), str)
            and bool(threshold["comparison"].strip())
        )
    return False
