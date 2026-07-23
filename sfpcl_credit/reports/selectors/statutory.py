from django.db.models import Sum

from sfpcl_credit.compliance.models import (
    NbfcPrincipalBusinessTest,
    Section186Tracker,
)
from sfpcl_credit.compliance.modules.compliance_control_tracker import (
    ComplianceDenied,
    require_auditor_scope,
)
from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
    NbfcPrincipalBusinessTestModule,
)
from sfpcl_credit.compliance.modules.section186_tracker import Section186TrackerModule
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import financial_year, reject_unknown
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


def select_section_186(*, actor, query_params):
    return _select(
        actor=actor,
        query_params=query_params,
        model=Section186Tracker,
        permission="compliance.section186.read",
        serializer=Section186TrackerModule.serialize,
        id_field="section_186_tracker_id",
        total_fields=("applicable_limit_amount", "total_loans_exposure_amount"),
    )


def select_nbfc_test(*, actor, query_params):
    return _select(
        actor=actor,
        query_params=query_params,
        model=NbfcPrincipalBusinessTest,
        permission="compliance.nbfc_test.read",
        serializer=NbfcPrincipalBusinessTestModule.serialize,
        id_field="nbfc_principal_test_id",
        total_fields=(),
    )


def _select(
    *,
    actor,
    query_params,
    model,
    permission,
    serializer,
    id_field,
    total_fields,
):
    reject_unknown(
        query_params,
        {"financial_year", "quarter", "review_status", "page", "page_size"},
    )
    require_permission(actor=actor, permission=permission)
    try:
        require_auditor_scope(actor)
    except ComplianceDenied as exc:
        raise ReportPermissionDenied from exc
    queryset = model.objects.select_related(
        "task",
        "evidence",
        "prepared_by_user",
        "reviewer_user",
    )
    year = query_params.get("financial_year")
    if year:
        financial_year(year)
        queryset = queryset.filter(financial_year=year)
    quarter = query_params.get("quarter")
    if quarter:
        if quarter not in {"Q1", "Q2", "Q3", "Q4"}:
            raise ReportValidation({"quarter": "Use Q1, Q2, Q3, or Q4."})
        queryset = queryset.filter(quarter=quarter)
    review_status = query_params.get("review_status")
    if review_status:
        if review_status not in {"draft", "pending", "accepted", "rejected"}:
            raise ReportValidation({"review_status": "Unsupported review status."})
        if review_status == "draft":
            queryset = queryset.filter(
                submitted_for_review_at__isnull=True,
                review_decision="",
            )
        elif review_status == "pending":
            queryset = queryset.filter(
                submitted_for_review_at__isnull=False,
                review_decision="",
            )
        else:
            queryset = queryset.filter(review_decision=review_status)
    totals = {
        field: queryset.aggregate(value=Sum(field))["value"]
        for field in total_fields
    }
    rows, pagination = paginate(
        queryset.order_by("financial_year", "quarter", id_field),
        query_params,
    )
    if total_fields:
        pagination["totals"] = {
            field: f"{(totals[field] or 0):.2f}" for field in total_fields
        }
    return [_report_projection(serializer(row, actor)) for row in rows], pagination


def _report_projection(data):
    return {
        key: value
        for key, value in data.items()
        if key not in {"available_actions", "board_document_id"}
    }
