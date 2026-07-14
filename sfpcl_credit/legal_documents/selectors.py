from math import ceil

from django.core.exceptions import ValidationError

from sfpcl_credit.legal_documents.models import LoanDocument


_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_LIST_PARAMS = {"page", "page_size"}


def list_for_application(*, application_id, query_params):
    """Return one strict, deterministic, exactly counted application page."""
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(
        _positive_int("page_size", query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
    )
    queryset = (
        LoanDocument.objects.select_related("document", "document_template")
        .filter(loan_application_id=application_id)
        .order_by("-created_at", "-loan_document_id")
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return list(queryset[offset : offset + page_size]), {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def latest_generated_metadata_by_type(*, application_id, document_types):
    """Return only retained, renderer-validated generation metadata."""
    rows = (
        LoanDocument.objects.filter(
            loan_application_id=application_id,
            document_type__in=document_types,
            generation_status=LoanDocument.GENERATION_GENERATED,
            document_template__isnull=False,
            document__isnull=False,
        )
        .order_by("document_type", "-created_at", "-loan_document_id")
        .values_list("document_type", "loan_document_id")
    )
    latest = {}
    for document_type, loan_document_id in rows:
        latest.setdefault(document_type, loan_document_id)
    return latest


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed < 1:
        raise ValidationError({field: "Must be a positive integer."})
    return parsed
