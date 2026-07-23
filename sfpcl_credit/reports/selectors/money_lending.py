from sfpcl_credit.compliance.modules.compliance_control_tracker import (
    ComplianceDenied,
    permission_codes,
    search_money_lending_reviews,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import financial_year, reject_unknown


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {"financial_year", "state", "applicability", "page", "page_size"},
    )
    permissions = permission_codes(actor)
    if not permissions.intersection(
        {"compliance.money_lending_review.manage", "compliance.task.read"}
    ):
        raise ReportPermissionDenied
    try:
        queryset = search_money_lending_reviews(actor=actor, search="")
    except ComplianceDenied as exc:
        raise ReportPermissionDenied from exc
    year = query_params.get("financial_year")
    if year:
        financial_year(year)
        queryset = queryset.filter(financial_year=year)
    state = query_params.get("state")
    if state:
        queryset = queryset.filter(state__iexact=state)
    applicability = query_params.get("applicability")
    if applicability:
        if applicability not in {"exempt", "applicable"}:
            raise ReportValidation({"applicability": "Unsupported applicability."})
        queryset = queryset.filter(applicability=applicability)
    rows, pagination = paginate(queryset, query_params)
    return [
        {
            "money_lending_law_review_id": str(row.pk),
            "financial_year": row.financial_year,
            "state": row.state,
            "applicability": row.applicability,
            "exemption_applicable_flag": row.exemption_applicable_flag,
            "compliance_task_id": str(row.task_id),
            "compliance_evidence_id": str(row.evidence_id),
            "reviewed_by_user_id": str(row.reviewed_by_user_id),
            "reviewed_at": row.reviewed_at.isoformat().replace("+00:00", "Z"),
        }
        for row in rows
    ], pagination
