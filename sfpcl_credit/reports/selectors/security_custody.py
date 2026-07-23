from sfpcl_credit.processes import security_instrument_evidence
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import reject_unknown
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission
from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    SH4ShareTransferForm,
)
from sfpcl_credit.security_instruments.modules import security_package


PERMISSION = "security.package.read"
INSTRUMENT_TYPES = {"sh4", "blank_dated_cheque"}


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {"instrument_type", "page", "page_size"},
    )
    require_permission(actor=actor, permission=PERMISSION)
    instrument_type = query_params.get("instrument_type")
    if instrument_type and instrument_type not in INSTRUMENT_TYPES:
        raise ReportValidation(
            {"instrument_type": "Use sh4 or blank_dated_cheque."}
        )
    rows = []
    if instrument_type in (None, "sh4"):
        rows.extend(_sh4_rows(actor))
    if instrument_type in (None, "blank_dated_cheque"):
        rows.extend(_cheque_rows(actor))
    rows.sort(
        key=lambda row: (
            row["_ordering_at"],
            row["instrument_type"],
            row["instrument_id"],
        ),
        reverse=True,
    )
    for row in rows:
        row.pop("_ordering_at")
    page_rows, pagination = paginate(rows, query_params)
    return list(page_rows), pagination


def _sh4_rows(actor):
    rows = []
    queryset = SH4ShareTransferForm.objects.select_related(
        "security_package",
    ).filter(form_status=SH4ShareTransferForm.STATUS_HELD_IN_CUSTODY)
    for form in queryset:
        package = _readable_package(actor, form.security_package)
        if package is None:
            continue
        public = package["sh4_share_transfer_form"]
        rows.append(
            _row(
                instrument_type="sh4",
                instrument_id=public["sh4_share_transfer_form_id"],
                package=package,
                member_id=public["member_id"],
                custody_status=public["form_status"],
                custody_location=public["custody_location"],
                updated_at=form.updated_at,
            )
        )
    return rows


def _cheque_rows(actor):
    rows = []
    queryset = BlankDatedCheque.objects.select_related(
        "security_package",
    ).filter(cheque_status=BlankDatedCheque.STATUS_HELD)
    for cheque in queryset:
        package = _readable_package(actor, cheque.security_package)
        if package is None:
            continue
        public = package["blank_dated_cheque"]
        rows.append(
            _row(
                instrument_type="blank_dated_cheque",
                instrument_id=public["blank_dated_cheque_id"],
                package=package,
                member_id=public["member_id"],
                custody_status=public["cheque_status"],
                custody_location=public["custody_location"],
                updated_at=cheque.updated_at,
            )
        )
    return rows


def _readable_package(actor, package):
    try:
        return security_instrument_evidence.read_package(
            actor=actor,
            application_id=package.loan_application_id,
        )
    except (security_package.AccessDenied, security_package.NotFound):
        return None


def _row(
    *,
    instrument_type,
    instrument_id,
    package,
    member_id,
    custody_status,
    custody_location,
    updated_at,
):
    return {
        "instrument_type": instrument_type,
        "instrument_id": instrument_id,
        "security_package_id": package["security_package_id"],
        "loan_application_id": package["loan_application_id"],
        "loan_account_id": package["loan_account_id"],
        "member_id": member_id,
        "custody_status": custody_status,
        "custody_location": custody_location,
        "custody_recorded_at": updated_at.isoformat().replace("+00:00", "Z"),
        "_ordering_at": updated_at,
    }
