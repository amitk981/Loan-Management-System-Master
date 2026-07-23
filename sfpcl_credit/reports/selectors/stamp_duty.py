from sfpcl_credit.approvals.modules import document_checklist_access
from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import DocumentChecklist, StampDutyRecord
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import inclusive_date_range, reject_unknown


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {"from_date", "to_date", "status", "stamp_type", "page", "page_size"},
    )
    checklists, error = document_checklist_access.scope_post_sanction_checklists(
        actor=actor,
        queryset=DocumentChecklist.objects.all(),
    )
    if error:
        raise ReportPermissionDenied
    if (
        "internal_auditor" in auth_service.effective_role_codes(actor)
        and not has_active_audit_read_scope(actor)
    ):
        raise ReportPermissionDenied
    application_ids = checklists.values("loan_application_id")
    if set(auth_service.effective_role_codes(actor)).intersection(
        {
            "compliance_team_member",
            "company_secretary",
            "credit_manager",
            "internal_auditor",
        }
    ):
        application_ids = LoanApplication.objects.filter(
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION
        ).values("pk")
    queryset = StampDutyRecord.objects.select_related(
        "loan_document__loan_application__member",
    ).filter(
        loan_document__loan_application_id__in=application_ids
    )
    from_date, to_date = inclusive_date_range(query_params)
    if from_date:
        queryset = queryset.filter(stamp_purchase_date__gte=from_date)
    if to_date:
        queryset = queryset.filter(stamp_purchase_date__lte=to_date)
    for field, allowed in (
        ("status", StampDutyRecord.STATUSES),
        ("stamp_type", StampDutyRecord.TYPES),
    ):
        value = query_params.get(field)
        if value:
            if value not in allowed:
                raise ReportValidation({field: f"Unsupported {field}."})
            queryset = queryset.filter(**{field: value})
    rows, pagination = paginate(
        queryset.order_by("-stamp_purchase_date", "-stamp_duty_record_id"),
        query_params,
    )
    return [_serialize(row) for row in rows], pagination


def _serialize(row):
    application = row.loan_document.loan_application
    return {
        "stamp_duty_record_id": str(row.pk),
        "loan_document_id": str(row.loan_document_id),
        "document_type": row.loan_document.document_type,
        "loan_application_id": str(application.pk),
        "application_reference_number": application.application_reference_number,
        "member_id": str(application.member_id),
        "borrower_name": application.member.display_name,
        "stamp_paper_amount": f"{row.stamp_paper_amount:.2f}",
        "stamp_type": row.stamp_type,
        "stamp_number": row.stamp_number,
        "stamp_purchase_date": (
            row.stamp_purchase_date.isoformat() if row.stamp_purchase_date else None
        ),
        "executed_date": row.executed_date.isoformat() if row.executed_date else None,
        "status": row.status,
        "notarisation_status": (
            row.loan_document.notarisation_record.status
            if hasattr(row.loan_document, "notarisation_record")
            else None
        ),
    }
