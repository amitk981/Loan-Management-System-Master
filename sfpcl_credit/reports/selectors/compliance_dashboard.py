from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.compliance.models import (
    NbfcPrincipalBusinessTest,
    Section186Tracker,
)
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.reports.errors import ReportPermissionDenied
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import financial_year, reject_unknown


PERMISSION = "reports.compliance.read"
OWNER_PERMISSIONS = {
    "compliance.section186.read",
    "compliance.nbfc_test.read",
}


def select(*, actor, query_params):
    reject_unknown(query_params, {"financial_year", "page", "page_size"})
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or PERMISSION not in permissions
        or not OWNER_PERMISSIONS.issubset(permissions)
    ):
        raise ReportPermissionDenied
    if (
        "internal_auditor" in actor.role_codes()
        and not has_active_audit_read_scope(actor)
    ):
        raise ReportPermissionDenied
    year = query_params.get("financial_year")
    if year:
        financial_year(year)
    section_rows = Section186Tracker.objects.all()
    nbfc_rows = NbfcPrincipalBusinessTest.objects.all()
    if year:
        section_rows = section_rows.filter(financial_year=year)
        nbfc_rows = nbfc_rows.filter(financial_year=year)
    rows = [
        *(_serialize_section(row) for row in section_rows.order_by("quarter", "section_186_tracker_id")),
        *(_serialize_nbfc(row) for row in nbfc_rows.order_by("quarter", "nbfc_principal_test_id")),
    ]
    return paginate(rows, query_params)


def _serialize_section(row):
    return {
        "report_type": "section_186",
        "report_record_id": str(row.pk),
        "financial_year": row.financial_year,
        "quarter": row.quarter,
        "applicable_limit_amount": f"{row.applicable_limit_amount:.2f}",
        "total_loans_exposure_amount": f"{row.total_loans_exposure_amount:.2f}",
        "headroom_amount": f"{row.headroom_amount:.2f}",
        "within_limit_flag": row.within_limit_flag,
        "special_resolution_required_flag": row.special_resolution_required_flag,
        "review_status": _review_status(row),
        "prepared_at": _timestamp(row.prepared_at),
    }


def _serialize_nbfc(row):
    return {
        "report_type": "nbfc_principal_business",
        "report_record_id": str(row.pk),
        "financial_year": row.financial_year,
        "quarter": row.quarter,
        "financial_asset_ratio": f"{row.financial_asset_ratio:.4f}",
        "financial_income_ratio": f"{row.financial_income_ratio:.4f}",
        "registration_triggered_flag": row.registration_triggered_flag,
        "one_ratio_above_statutory_flag": row.one_ratio_above_statutory_flag,
        "early_warning_flag": row.early_warning_flag,
        "review_status": _review_status(row),
        "prepared_at": _timestamp(row.prepared_at),
    }


def _review_status(row):
    return row.review_decision or (
        "pending" if row.submitted_for_review_at else "draft"
    )


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z")
