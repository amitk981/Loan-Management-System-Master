from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from sfpcl_credit.reports.errors import ReportValidation


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def paginate(queryset, query_params):
    page_number = _positive_int(query_params.get("page"), "page", 1)
    page_size = _positive_int(
        query_params.get("page_size"),
        "page_size",
        DEFAULT_PAGE_SIZE,
    )
    if page_size > MAX_PAGE_SIZE:
        raise ReportValidation(
            {"page_size": f"Must be at most {MAX_PAGE_SIZE}."}
        )
    paginator = Paginator(queryset, page_size)
    try:
        page = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger) as exc:
        raise ReportValidation({"page": "Must identify an existing page."}) from exc
    return tuple(page.object_list), {
        "page": page.number,
        "page_size": page_size,
        "total_count": paginator.count,
        "total_pages": paginator.num_pages,
        "has_next": page.has_next(),
        "has_previous": page.has_previous(),
    }


def _positive_int(raw_value, field, default):
    if raw_value in (None, ""):
        return default
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ReportValidation({field: "Must be a positive integer."}) from exc
    if parsed < 1:
        raise ReportValidation({field: "Must be a positive integer."})
    return parsed
