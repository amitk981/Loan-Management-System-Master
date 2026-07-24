import hashlib
import json
from pathlib import Path
import subprocess
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PYTHON = str(Path(sys.prefix) / "bin" / "python")

LOCAL_TEST_LABELS = {
    "PERF-001": "sfpcl_credit.tests.test_auth_api.AuthApiTests.test_active_user_can_login_and_receives_tokens",
    "PERF-002": "sfpcl_credit.tests.test_dashboard_api.DashboardApiTests.test_credit_manager_pending_completeness_card_reconciles_to_scoped_application_list",
    "PERF-003": "sfpcl_credit.tests.test_member_directory_api.MemberDirectoryApiTests.test_member_directory_supports_source_filters_and_search",
    "PERF-004": "sfpcl_credit.tests.test_loan_applications_api.LoanApplicationDraftApiTests.test_create_and_read_draft_returns_metadata_only_response_and_audit",
    "PERF-005": "sfpcl_credit.tests.test_document_files_api.DocumentFilesApiTests.test_authenticated_upload_stores_file_metadata_checksum_and_audit",
    "PERF-006": "sfpcl_credit.tests.test_approval_case_routing_api.ApprovalCaseRoutingApiTests.test_assigned_approver_can_record_partial_approval_through_canonical_case_projection",
    "PERF-007": "sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_worker_completes_csv_and_status_issues_an_expiring_download",
    "PERF-008": "sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome",
    "PERF-009": "sfpcl_credit.tests.test_interest_accrual_api.MonthlyInterestAccrualApiTests.test_bulk_dry_run_reports_calculated_outcome_without_any_write",
    "PERF-010": "sfpcl_credit.tests.test_audit_explorer_api.AuditExplorerApiTests.test_large_page_has_bounded_queries_and_stable_tie_break_order",
    "TARGET-LOGIN": "sfpcl_credit.tests.test_auth_api.AuthApiTests.test_active_user_can_login_and_receives_tokens",
    "TARGET-DASHBOARD": "sfpcl_credit.tests.test_dashboard_api.DashboardApiTests.test_credit_manager_pending_completeness_card_reconciles_to_scoped_application_list",
    "TARGET-MEMBER-SEARCH": "sfpcl_credit.tests.test_member_directory_api.MemberDirectoryApiTests.test_member_directory_supports_source_filters_and_search",
    "TARGET-APPLICATION-DETAIL": "sfpcl_credit.tests.test_loan_applications_api.LoanApplicationDraftApiTests.test_staff_application_detail_returns_neutral_owner_and_authorized_actions",
    "TARGET-LOAN-ACCOUNT-360": "sfpcl_credit.tests.test_loan_account_reads_api.ActiveLoanAccountReadApiTests.test_exact_transfer_projects_active_funded_amounts_and_activation_time",
    "TARGET-APPROVAL-ACTION": "sfpcl_credit.tests.test_approval_case_routing_api.ApprovalCaseRoutingApiTests.test_assigned_approver_can_record_partial_approval_through_canonical_case_projection",
    "TARGET-DISBURSEMENT-READINESS": "sfpcl_credit.tests.test_disbursement_readiness_api.DisbursementReadinessApiTests.test_all_current_owner_decisions_return_ready",
    "TARGET-DOCUMENT-UPLOAD": "sfpcl_credit.tests.test_document_files_api.DocumentFilesApiTests.test_authenticated_upload_stores_file_metadata_checksum_and_audit",
    "TARGET-REPORT-EXPORT": "sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_worker_completes_csv_and_status_issues_an_expiring_download",
    "TARGET-DPD-BATCH": "sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome",
    "TARGET-MONTHLY-ACCRUAL": "sfpcl_credit.tests.test_interest_accrual_api.MonthlyInterestAccrualApiTests.test_bulk_dry_run_reports_calculated_outcome_without_any_write",
    "TARGET-CAPITALISATION-DRY-RUN": "sfpcl_credit.tests.test_interest_capitalisation_api.InterestCapitalisationApiTests.test_preview_derives_eligible_unpaid_interest_and_is_zero_write",
    "PROBE-SUSTAINED-WORKFLOW": "sfpcl_credit.tests.test_loan_applications_api.LoanApplicationDraftApiTests.test_epic_006_cross_role_happy_path_reaches_one_pending_sanction_case",
    "PROBE-LARGE-DOCUMENT-VOLUME": "sfpcl_credit.tests.test_document_files_api.DocumentFilesApiTests.test_authenticated_upload_stores_file_metadata_checksum_and_audit",
    "PROBE-LARGE-AUDIT-TABLE": "sfpcl_credit.tests.test_audit_explorer_api.AuditExplorerApiTests.test_large_page_has_bounded_queries_and_stable_tie_break_order",
    "PROBE-HEAVY-EXPORT-QUEUE": "sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_worker_completes_csv_and_status_issues_an_expiring_download",
    "PROBE-WORKER-RESTART": "sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_generation_failure_is_terminal_observable_and_retry_safe",
    "PROBE-REDIS-RESTART": "sfpcl_credit.tests.test_report_exports_api.ReportExportApiTests.test_request_and_replay_return_one_queued_job_for_canonical_identity",
    "PROBE-DATABASE-PRESSURE": "sfpcl_credit.tests.test_dashboard_api.DashboardApiTests.test_each_supported_role_uses_a_bounded_dashboard_query_budget",
}


def run_bounded_local(*, scenarios, run=subprocess.run):
    labels = sorted({LOCAL_TEST_LABELS[row["scenario_id"]] for row in scenarios})
    total_runs = max(
        row["warm_up_repetitions"] + row["measured_repetitions"]
        for row in scenarios
    )
    completed = run(
        [
            BACKEND_PYTHON,
            "sfpcl_credit/manage.py",
            "test",
            *labels,
            "--keepdb",
            "--testrunner",
            "sfpcl_credit.performance_readiness.timed_runner.PerformanceTimingRunner",
        ],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    timings = _parse_timings(completed.stdout)
    failed = (
        completed.returncode != 0
        or set(timings) != set(labels)
        or any(len(samples) != total_runs for samples in timings.values())
    )

    results = []
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        samples = timings.get(
            LOCAL_TEST_LABELS[scenario_id],
            [0.0] * total_runs,
        )[
            : scenario["warm_up_repetitions"]
            + scenario["measured_repetitions"]
        ]
        if failed:
            status = "fail"
        elif scenario["threshold"]["kind"] == "maximum_seconds":
            status = "pass"
        else:
            status = "release-evidence-required"
        raw = json.dumps(
            {"samples": samples, "status": status},
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        results.append(
            {
                "scenario_id": scenario_id,
                "status": status,
                "samples": samples,
                "raw_result_sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return results


def _parse_timings(output):
    prefix = "PERFORMANCE_TIMINGS_JSON="
    for line in reversed(output.splitlines()):
        if line.startswith(prefix):
            payload = json.loads(line[len(prefix):])
            if isinstance(payload, dict):
                return {
                    label: [round(value, 6) for value in values]
                    for label, values in payload.items()
                    if isinstance(values, list)
                }
    return {}
