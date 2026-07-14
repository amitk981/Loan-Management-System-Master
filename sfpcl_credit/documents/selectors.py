from math import ceil

from django.core.exceptions import ValidationError

from sfpcl_credit.documents.models import DocumentTemplate


_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_LIST_PARAMS = {
    "page",
    "page_size",
    "document_type",
    "borrower_type",
    "approval_status",
}


def list_document_templates(query_params):
    """Shape the strict, bounded document-template catalogue query."""
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {key: "Unknown query parameter." for key in sorted(unknown)}
        )
    queryset = DocumentTemplate.objects.select_related("template_file")
    for field in ("document_type", "approval_status"):
        value = query_params.get(field)
        if value:
            if (
                field == "approval_status"
                and value not in DocumentTemplate.APPROVAL_STATUSES
            ):
                raise ValidationError(
                    {"approval_status": "Must be one of draft, approved, retired."}
                )
            queryset = queryset.filter(**{field: value})
    if "borrower_type" in query_params:
        value = query_params.get("borrower_type")
        if value in ("", "null"):
            queryset = queryset.filter(borrower_type__isnull=True)
        elif value not in DocumentTemplate.BORROWER_TYPES:
            raise ValidationError(
                {"borrower_type": "Must be individual_farmer, fpc, fpo, or null."}
            )
        else:
            queryset = queryset.filter(borrower_type=value)
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(
        _positive_int("page_size", query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
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


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed <= 0:
        raise ValidationError({field: "Must be a positive integer."})
    return parsed
