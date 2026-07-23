from django.db.models import Q

from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.closure.models import LoanClosure
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import inclusive_date_range, reject_unknown
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {"from_date", "to_date", "closure_stage", "page", "page_size"},
    )
    require_permission(actor=actor, permission="closure.readiness.read")
    roles = set(auth_service.effective_role_codes(actor))
    scope = Q(pk__in=[])
    if "credit_manager" in roles:
        scope |= Q(loan_account__loan_account_status="closed")
    if "company_secretary" in roles:
        scope |= Q(
            loan_account__loan_application__application_status="approved_by_sanction"
        )
    if "internal_auditor" in roles:
        if not ApprovalCaseReadScopeGrant.objects.filter(
            role__role_code="internal_auditor",
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        ).exists():
            raise ReportPermissionDenied
        scope = Q()
    if not roles.intersection({"credit_manager", "company_secretary", "internal_auditor"}):
        raise ReportPermissionDenied
    queryset = LoanClosure.objects.select_related(
        "loan_account__member",
        "noc",
        "archive_record",
        "security_return",
    ).filter(scope)
    from_date, to_date = inclusive_date_range(query_params)
    if from_date:
        queryset = queryset.filter(closed_at__date__gte=from_date)
    if to_date:
        queryset = queryset.filter(closed_at__date__lte=to_date)
    stage = query_params.get("closure_stage")
    if stage:
        if stage != LoanClosure.STAGE_FINANCIALLY_CLOSED:
            raise ReportValidation({"closure_stage": "Unsupported closure stage."})
        queryset = queryset.filter(closure_stage=stage)
    rows, pagination = paginate(
        queryset.order_by("-closed_at", "-loan_closure_id"),
        query_params,
    )
    return [_serialize(row) for row in rows], pagination


def _serialize(row):
    noc = row.noc if hasattr(row, "noc") else None
    archive = row.archive_record if hasattr(row, "archive_record") else None
    security_return = (
        row.security_return if hasattr(row, "security_return") else None
    )
    return {
        "loan_closure_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_account_number": row.loan_account.loan_account_number,
        "member_id": str(row.loan_account.member_id),
        "borrower_name": row.loan_account.member.display_name,
        "closure_type": row.closure_type,
        "closure_stage": row.closure_stage,
        "closed_at": row.closed_at.isoformat().replace("+00:00", "Z"),
        "noc_id": str(noc.pk) if noc else None,
        "noc_issued_at": (
            noc.issued_at.isoformat().replace("+00:00", "Z") if noc else None
        ),
        "noc_delivery_status": noc.delivery_status if noc else None,
        "security_return_status": (
            security_return.return_status if security_return else None
        ),
        "archive_record_id": str(archive.pk) if archive else None,
        "retention_until_date": (
            archive.retention_until_date.isoformat() if archive else None
        ),
    }
