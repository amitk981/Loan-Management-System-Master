from dataclasses import dataclass

from sfpcl_credit.security_instruments.models import (
    SecurityPackage,
)


@dataclass(frozen=True)
class SecurityReadinessFacts:
    security_package_complete: bool
    poa_complete: bool
    sh4_complete: bool
    cdsl_pledge_complete: bool
    blank_dated_cheque_received: bool


def resolve_security_readiness(*, application_id, terminal_item_completed=lambda _code: False):
    """Project only terminal security evidence reconciled by the checklist owner."""
    package = (
        SecurityPackage.objects.select_for_update()
        .filter(loan_application_id=application_id)
        .first()
    )
    if package is None:
        return SecurityReadinessFacts(False, False, False, False, False)
    poa_complete = terminal_item_completed("poa")
    sh4_complete = (
        not package.physical_share_security_required_flag
        or terminal_item_completed("sh4")
    )
    cdsl_complete = (
        not package.demat_pledge_required_flag
        or terminal_item_completed("cdsl_pledge")
    )
    cheque_complete = terminal_item_completed("blank_dated_cheque")
    cancelled_complete = terminal_item_completed("cancelled_cheque")
    return SecurityReadinessFacts(
        security_package_complete=all((
            poa_complete, sh4_complete, cdsl_complete,
            cheque_complete, cancelled_complete,
        )),
        poa_complete=poa_complete,
        sh4_complete=sh4_complete,
        cdsl_pledge_complete=cdsl_complete,
        blank_dated_cheque_received=cheque_complete,
    )


__all__ = ["SecurityReadinessFacts", "resolve_security_readiness"]
