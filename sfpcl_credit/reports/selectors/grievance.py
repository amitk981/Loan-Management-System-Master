from sfpcl_credit.compliance.modules.compliance_control_tracker import (
    ComplianceDenied,
    ComplianceInvalid,
)
from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation


def select(*, actor, query_params):
    try:
        rows, pagination = GrievanceWorkflow.list(
            actor=actor,
            query=query_params,
        )
    except ComplianceDenied as exc:
        raise ReportPermissionDenied from exc
    except ComplianceInvalid as exc:
        raise ReportValidation(exc.field_errors) from exc
    return [_projection(row) for row in rows], pagination


def _projection(row):
    return {
        key: row[key]
        for key in (
            "grievance_id",
            "grievance_reference",
            "member_id",
            "loan_account_id",
            "loan_application_id",
            "grievance_category",
            "subject",
            "received_date",
            "received_channel",
            "resolution_due_date",
            "status",
            "tat_days",
            "days_overdue",
            "is_overdue",
            "resolution_summary",
            "closed_at",
            "borrower_informed",
        )
    }
