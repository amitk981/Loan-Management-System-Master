import re
from datetime import date

from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.reports.errors import ReportValidation


FINANCIAL_YEAR_PATTERN = re.compile(r"^FY(\d{4})-(\d{2})$")


def reject_unknown(query_params, allowed):
    unknown = sorted(set(query_params) - set(allowed))
    if unknown:
        raise ReportValidation(
            {field: "Unknown query parameter." for field in unknown}
        )


def optional_date(query_params, field, default=None):
    raw_value = query_params.get(field)
    if raw_value in (None, ""):
        return default
    try:
        parsed = parse_date(raw_value)
    except ValueError:
        parsed = None
    if parsed is None:
        raise ReportValidation({field: "Use YYYY-MM-DD."})
    return parsed


def inclusive_date_range(query_params):
    from_date = optional_date(query_params, "from_date")
    to_date = optional_date(query_params, "to_date")
    if from_date and to_date and from_date > to_date:
        raise ReportValidation(
            {"to_date": "Must be on or after from_date."}
        )
    return from_date, to_date


def as_of_date(query_params):
    return optional_date(
        query_params,
        "as_of_date",
        default=timezone.localdate(),
    )


def financial_year(value):
    match = FINANCIAL_YEAR_PATTERN.fullmatch(value or "")
    if match is None:
        raise ReportValidation(
            {"financial_year": "Use FYyyyy-yy, for example FY2026-27."}
        )
    start_year = int(match.group(1))
    if int(match.group(2)) != (start_year + 1) % 100:
        raise ReportValidation(
            {"financial_year": "The ending year must follow the starting year."}
        )
    return date(start_year, 4, 1), date(start_year + 1, 3, 31)
