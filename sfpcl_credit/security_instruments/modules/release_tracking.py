"""Owner interface exposing security identities eligible for closure release."""

from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    CDSLSharePledge,
    PowerOfAttorney,
    SH4ShareTransferForm,
)


class ReleaseSourceUnavailable(Exception):
    pass


def resolve_release_sources(*, package, for_update=False):
    """Return owned source records; never infer a required item from caller data."""
    queryset = lambda model: model.objects.select_for_update() if for_update else model.objects
    specifications = (
        (
            "sh4",
            package.physical_share_security_required_flag,
            SH4ShareTransferForm,
        ),
        ("blank_cheque", package.blank_cheque_required_flag, BlankDatedCheque),
        ("poa", package.poa_required_flag, PowerOfAttorney),
        ("cdsl", package.demat_pledge_required_flag, CDSLSharePledge),
    )
    sources = {}
    for item_type, required, model in specifications:
        source = queryset(model).filter(security_package=package).first()
        if required and source is None:
            raise ReleaseSourceUnavailable(
                f"The applicable {item_type} instrument is missing from its security owner."
            )
        sources[item_type] = source
    return sources


def validate_release_result(*, item_type, source, outcome):
    """Validate source owner state before closure retains a release result."""
    if item_type == "sh4":
        eligible = source.form_status == SH4ShareTransferForm.STATUS_HELD_IN_CUSTODY
    elif item_type == "blank_cheque":
        eligible = source.cheque_status == BlankDatedCheque.STATUS_HELD
    elif item_type == "poa":
        eligible = (
            source.status == PowerOfAttorney.STATUS_ACTIVE
            and source.execution_status == PowerOfAttorney.EXECUTION_EXECUTED
        )
    else:
        eligible = (
            source.pledge_status == CDSLSharePledge.STATUS_CREATED
            and source.pledge_acceptance_status == CDSLSharePledge.ACCEPTANCE_ACCEPTED
        )
    if not eligible:
        raise ReleaseSourceUnavailable(
            f"The {item_type} instrument is not in an owner-confirmed releasable state."
        )
    allowed = {
        "sh4": {"pending", "returned"},
        "blank_cheque": {"pending", "returned"},
        "poa": {"pending", "released"},
        "cdsl": {"pending", "rejected", "completed"},
    }[item_type]
    if outcome not in allowed:
        raise ReleaseSourceUnavailable(
            f"The {outcome} outcome is invalid for {item_type}."
        )
    return {
        "custody_location": getattr(source, "custody_location", None),
        "psn": getattr(source, "pledge_sequence_number", None),
        "pledgor_bo_account": (
            f"************{source.pledgor_bo_account_last4}"
            if item_type == "cdsl"
            else None
        ),
        "pledgee_bo_account": (
            f"************{source.pledgee_bo_account_last4}"
            if item_type == "cdsl" and source.pledgee_bo_account_last4
            else None
        ),
    }
