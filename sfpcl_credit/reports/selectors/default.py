from sfpcl_credit.defaults.modules.default_workflow import (
    DefaultPermissionDenied,
    DefaultValidation,
    list_default_cases,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation


def select(*, actor, query_params):
    try:
        return list_default_cases(actor=actor, query_params=query_params)
    except DefaultValidation as exc:
        raise ReportValidation(exc.field_errors) from exc
    except DefaultPermissionDenied as exc:
        raise ReportPermissionDenied from exc
