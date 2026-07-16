"""Page-bounded selector for the S26 staff documentation queue."""
from django.core.paginator import Paginator
from sfpcl_credit.approvals.modules import document_checklist_access
from sfpcl_credit.legal_documents.models import DocumentChecklist
QUEUE_PAGE_SIZE = 20

def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default

def _visible_checklists(actor, access_denied):
    queryset = DocumentChecklist.objects.all().select_related('loan_application__member', 'loan_application__security_package__power_of_attorney', 'loan_application__security_package__sh4_share_transfer_form', 'loan_application__security_package__cdsl_share_pledge', 'loan_application__security_package__blank_dated_cheque').prefetch_related('items').order_by('created_at', 'document_checklist_id')
    scoped, error_code = document_checklist_access.scope_post_sanction_checklists(actor=actor, queryset=queryset)
    if error_code:
        raise access_denied(error_code)
    return scoped

def list_queue(*, actor, query_params, projector, access_denied):
    page_size = min(_positive_int(query_params.get('page_size'), QUEUE_PAGE_SIZE), QUEUE_PAGE_SIZE)
    paginator = Paginator(_visible_checklists(actor, access_denied), page_size)
    page = paginator.get_page(_positive_int(query_params.get('page'), 1))
    rows = projector(actor=actor, checklists=tuple(page.object_list))
    return {'items': rows, 'pagination': {'page': page.number, 'page_size': page_size, 'total_count': paginator.count, 'total_pages': paginator.num_pages, 'has_next': page.has_next(), 'has_previous': page.has_previous()}}
