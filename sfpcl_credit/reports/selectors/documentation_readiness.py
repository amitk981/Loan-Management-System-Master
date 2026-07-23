from sfpcl_credit.approvals.modules import document_checklist_access
from sfpcl_credit.legal_documents.models import ChecklistItem, DocumentChecklist
from sfpcl_credit.reports.errors import (
    ReportPermissionDenied,
    ReportValidation,
)
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import reject_unknown


def select(*, actor, query_params):
    reject_unknown(query_params, {"status", "page", "page_size"})
    queryset, error_code = document_checklist_access.scope_post_sanction_checklists(
        actor=actor,
        queryset=DocumentChecklist.objects.select_related(
            "loan_application__member"
        ).prefetch_related("items"),
    )
    if error_code:
        raise ReportPermissionDenied
    status = query_params.get("status")
    if status:
        if status == "pending":
            queryset = queryset.exclude(
                checklist_status=DocumentChecklist.STATUS_READY
            )
        elif status not in DocumentChecklist.STATUSES:
            raise ReportValidation({"status": "Unsupported checklist status."})
        else:
            queryset = queryset.filter(checklist_status=status)
    rows, pagination = paginate(
        queryset.order_by("-updated_at", "-document_checklist_id"),
        query_params,
    )
    return [_serialize(row) for row in rows], pagination


def _serialize(row):
    required_items = [
        item
        for item in row.items.all()
        if item.required_flag and item.applicable_flag
    ]
    completed = [
        item
        for item in required_items
        if item.completion_status == ChecklistItem.STATUS_COMPLETE
    ]
    pending = [
        item
        for item in required_items
        if item.completion_status == ChecklistItem.STATUS_PENDING
    ]
    application = row.loan_application
    return {
        "document_checklist_id": str(row.pk),
        "loan_application_id": str(row.loan_application_id),
        "application_reference_number": application.application_reference_number,
        "member_id": str(application.member_id),
        "borrower_name": application.member.display_name,
        "checklist_status": row.checklist_status,
        "required_item_count": len(required_items),
        "completed_item_count": len(completed),
        "pending_item_count": len(pending),
        "blocker_codes": [item.item_code for item in pending],
        "created_at": _timestamp(row.created_at),
        "updated_at": _timestamp(row.updated_at),
    }


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z")
