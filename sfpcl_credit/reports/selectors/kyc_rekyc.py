from sfpcl_credit.compliance.modules.compliance_control_tracker import (
    ComplianceDenied,
    ComplianceInvalid,
)
from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation


def select(*, actor, query_params):
    try:
        rows, pagination = KYCReviewTracker.list_reviews(
            actor=actor,
            query=query_params,
        )
    except (ComplianceDenied, PermissionError) as exc:
        raise ReportPermissionDenied from exc
    except ComplianceInvalid as exc:
        raise ReportValidation(exc.field_errors) from exc
    return [_projection(row) for row in rows], pagination


def _projection(row):
    completeness = row.get("completeness") or {}
    return {
        "kyc_review_id": row["kyc_review_id"],
        "member_id": row["member_id"],
        "member_name": row["member_name"],
        "member_type": row["member_type"],
        "member_status": row["member_status"],
        "kyc_status": row["kyc_status"],
        "risk_rating": row["risk_rating"],
        "due_date": row["due_date"],
        "days_overdue": row["days_overdue"],
        "status": row["status"],
        "pan_status": "verified" if completeness.get("pan_verified") else "missing",
        "aadhaar_status": (
            "verified" if completeness.get("aadhaar_verified") else "missing"
        ),
        "ckyc_consent": bool(completeness.get("ckyc_consent")),
    }
