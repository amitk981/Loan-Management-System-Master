"""Central fail-closed report export policy.

The request, worker, status, and download paths all cross this module's interface.
Selectors remain the authority for object scope and which fields can be emitted.
"""

import re
from dataclasses import dataclass

from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.shared.audit_text import (
    SAFE_AUDIT_TEXT_ERROR,
    UnsafeAuditText,
    safe_audit_text,
)


EXPORT_PERMISSION = "reports.export"
SENSITIVE_EXPORT_PERMISSION = "reports.export_sensitive"

REPORT_CLASSIFICATIONS = {
    "application-pipeline": "confidential",
    "documentation-readiness": "confidential",
    "loan-portfolio": "confidential",
    "dpd": "confidential",
    "disbursement-pending": "confidential",
    "compliance-dashboard": "restricted",
    "section-186": "confidential",
    "nbfc-test": "confidential",
    "credit-sanction": "confidential",
    "default": "restricted",
    "exception": "restricted",
    "security-custody": "restricted",
    "sap-pending": "confidential",
    "disbursement": "confidential",
    "repayment": "confidential",
    "recovery": "critical_restricted",
    "closure-noc": "confidential",
    "kyc-rekyc": "restricted",
    "stamp-duty": "confidential",
    "money-lending-review": "confidential",
    "grievance": "restricted",
    "interest-invoice": "confidential",
    "interest-accrual": "confidential",
    "cfo-quarterly-mis": "confidential",
    "audit-log-export": "restricted",
}

_COLUMN_CODE = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
_MASKED_VALUE = re.compile(r"^[A-Za-z0-9]*\*+[A-Za-z0-9]*$")


@dataclass(frozen=True)
class ExportDecision:
    classification: str
    requested_columns: tuple[str, ...]
    sensitive_export: bool
    sensitive_reason: str | None
    authority_snapshot: dict


def evaluate_request(*, actor, report_code, columns, sensitive_reason_supplied, sensitive_reason):
    """Authorise a request without trusting client role, scope, or column claims."""
    classification = REPORT_CLASSIFICATIONS.get(report_code)
    if classification is None:
        raise ReportPermissionDenied
    permissions = _permissions(actor)
    if EXPORT_PERMISSION not in permissions:
        raise ReportPermissionDenied
    requested_columns = _requested_columns(columns)
    reason = None
    if sensitive_reason_supplied:
        if SENSITIVE_EXPORT_PERMISSION not in permissions:
            raise ReportPermissionDenied
        try:
            reason = safe_audit_text(sensitive_reason, max_length=500)
        except UnsafeAuditText as exc:
            raise ReportValidation({"sensitive_reason": SAFE_AUDIT_TEXT_ERROR}) from exc
        if report_code == "kyc-rekyc":
            # The source leaves the required highest authority unresolved.
            raise ReportPermissionDenied
    return ExportDecision(
        classification=classification,
        requested_columns=requested_columns,
        sensitive_export=sensitive_reason_supplied,
        sensitive_reason=reason,
        authority_snapshot=_authority_snapshot(
            actor=actor,
            permissions=permissions,
            sensitive_export=sensitive_reason_supplied,
        ),
    )


def require_current_access(*, actor, job):
    permissions = _permissions(actor)
    required = {EXPORT_PERMISSION}
    if job.sensitive_export:
        required.add(SENSITIVE_EXPORT_PERMISSION)
    if not required.issubset(permissions):
        raise ReportPermissionDenied
    if REPORT_CLASSIFICATIONS.get(job.report_code) != job.classification:
        raise ReportPermissionDenied


def project_rows(*, job, rows):
    """Return selector-owned permitted columns with sensitive values policy-projected."""
    server_columns = {key for row in rows for key in row if _COLUMN_CODE.fullmatch(key)}
    if job.requested_columns:
        columns = [
            column for column in job.requested_columns if column in server_columns
        ]
    else:
        columns = sorted(server_columns)
    projected = []
    for row in rows:
        projected.append(
            {
                column: _project_value(
                    column,
                    row.get(column),
                    sensitive_export=job.sensitive_export,
                )
                for column in columns
            }
        )
    return projected, columns


def _permissions(actor):
    if not actor.can_authenticate():
        raise ReportPermissionDenied
    return set(auth_service.effective_permission_codes(actor))


def _requested_columns(columns):
    if columns is None:
        return ()
    if not isinstance(columns, list) or not columns:
        raise ReportValidation({"columns": "Must be a non-empty list of column codes."})
    if len(columns) > 100:
        raise ReportValidation({"columns": "At most 100 columns may be requested."})
    requested = []
    for value in columns:
        if not isinstance(value, str) or not _COLUMN_CODE.fullmatch(value):
            raise ReportValidation(
                {"columns": "Each column must be a valid server column code."}
            )
        if value not in requested:
            requested.append(value)
    return tuple(requested)


def _authority_snapshot(*, actor, permissions, sensitive_export):
    return {
        "actor_id": str(actor.pk),
        "role_codes": sorted(auth_service.effective_role_codes(actor)),
        "team_codes": sorted(actor.team_codes()),
        "reports_export": EXPORT_PERMISSION in permissions,
        "reports_export_sensitive": SENSITIVE_EXPORT_PERMISSION in permissions,
        "sensitive_export": sensitive_export,
    }


def _project_value(column, value, *, sensitive_export):
    family = _sensitive_family(column)
    if family is None or sensitive_export or value is None:
        return value
    text = str(value)
    if _MASKED_VALUE.fullmatch(text):
        return text
    if family == "pan":
        return f"{text[:5]}****{text[-1:]}" if len(text) >= 6 else "****"
    if family == "aadhaar":
        return f"{'*' * max(len(text) - 4, 8)}{text[-4:]}"
    if family in {"bank_account", "bo_account"}:
        return f"{'*' * max(len(text) - 4, 12)}{text[-4:]}"
    if family == "cheque":
        return f"{'*' * max(len(text) - 2, 4)}{text[-2:]}"
    raise AssertionError("Unhandled sensitive export family.")


def _sensitive_family(column):
    normalized = column.lower()
    if "aadhaar" in normalized:
        return "aadhaar"
    if "bo_account" in normalized or (
        normalized.startswith(("pledgor_bo_", "pledgee_bo_"))
    ):
        return "bo_account"
    if "cheque" in normalized and (
        "number" in normalized or normalized.endswith("_no")
    ):
        return "cheque"
    if "bank_account" in normalized or normalized == "account_number":
        return "bank_account"
    if normalized in {"pan", "pan_number"} or normalized.endswith("_pan_number"):
        return "pan"
    return None

