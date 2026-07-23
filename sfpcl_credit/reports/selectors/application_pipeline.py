from django.db.models import Q

from sfpcl_credit.applications.models import (
    LoanApplication,
    LoanRequestRegisterEntry,
)
from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import inclusive_date_range, reject_unknown


PERMISSION = "reports.application_pipeline.read"


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {
            "from_date",
            "to_date",
            "status",
            "stage",
            "page",
            "page_size",
        },
    )
    permissions = set(auth_service.effective_permission_codes(actor))
    if not actor.can_authenticate() or PERMISSION not in permissions:
        raise ReportPermissionDenied
    queryset = LoanRequestRegisterEntry.objects.select_related(
        "loan_application",
        "member",
    )
    if "internal_auditor" in actor.role_codes():
        if not has_active_audit_read_scope(actor):
            raise ReportPermissionDenied
    elif "credit_manager" in actor.role_codes():
        queryset = queryset.filter(
            Q(current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT)
            | Q(loan_application__created_by_user=actor)
            | Q(loan_application__received_by_user=actor)
        )
    else:
        queryset = queryset.filter(
            Q(loan_application__created_by_user=actor)
            | Q(loan_application__received_by_user=actor)
        )
    from_date, to_date = inclusive_date_range(query_params)
    if from_date:
        queryset = queryset.filter(date_received__gte=from_date)
    if to_date:
        queryset = queryset.filter(date_received__lte=to_date)
    status = query_params.get("status")
    if status:
        if status != LoanRequestRegisterEntry.STATUS_REFERENCE_GENERATED:
            raise ReportValidation(
                {"status": "Unsupported loan request register status."}
            )
        queryset = queryset.filter(register_status=status)
    stage = query_params.get("stage")
    if stage:
        if stage not in {
            LoanApplication.STAGE_INITIAL,
            LoanApplication.STAGE_CREDIT_ASSESSMENT,
        }:
            raise ReportValidation({"stage": "Unsupported application stage."})
        queryset = queryset.filter(current_stage=stage)
    rows, pagination = paginate(
        queryset.order_by(
            "-date_received",
            "-loan_request_register_entry_id",
        ),
        query_params,
    )
    return [_serialize(row) for row in rows], pagination


def _serialize(row):
    return {
        "loan_request_register_entry_id": str(row.pk),
        "loan_application_id": str(row.loan_application_id),
        "application_reference_number": row.application_reference_number,
        "member_id": str(row.member_id),
        "borrower_name": row.borrower_name,
        "date_received": row.date_received.isoformat(),
        "reference_generated_date": row.reference_generated_date.isoformat(),
        "received_channel": row.received_channel,
        "register_status": row.register_status,
        "requested_amount": (
            f"{row.requested_amount:.2f}"
            if row.requested_amount is not None
            else None
        ),
        "declared_purpose": row.declared_purpose,
        "purpose_category": row.purpose_category,
        "member_type": row.member_type,
        "current_stage": row.current_stage,
        "current_owner_role": row.current_owner_role,
        "eligibility_status": row.eligibility_status,
        "sanction_status": row.sanction_status,
        "documentation_status": row.documentation_status,
        "disbursement_status": row.disbursement_status,
    }
