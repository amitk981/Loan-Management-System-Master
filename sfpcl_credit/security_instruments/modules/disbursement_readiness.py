from dataclasses import dataclass

from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    CDSLSharePledge,
    PowerOfAttorney,
    SH4ShareTransferForm,
    SecurityPackage,
)


@dataclass(frozen=True)
class SecurityReadinessFacts:
    security_package_complete: bool
    poa_complete: bool
    sh4_complete: bool
    cdsl_pledge_complete: bool
    blank_dated_cheque_received: bool


def resolve_security_readiness(*, application_id):
    """Project security-owner terminal states with conditional paths explicit."""
    package = (
        SecurityPackage.objects.select_for_update()
        .filter(loan_application_id=application_id)
        .first()
    )
    if package is None:
        return SecurityReadinessFacts(False, False, False, False, False)
    poa = PowerOfAttorney.objects.select_for_update().filter(
        security_package=package
    ).first()
    sh4 = SH4ShareTransferForm.objects.select_for_update().filter(
        security_package=package
    ).first()
    cdsl = CDSLSharePledge.objects.select_for_update().filter(
        security_package=package
    ).first()
    cheque = BlankDatedCheque.objects.select_for_update().filter(
        security_package=package
    ).first()
    return SecurityReadinessFacts(
        security_package_complete=(
            package.security_status == SecurityPackage.STATUS_COMPLETE
        ),
        poa_complete=bool(
            poa
            and poa.execution_status == PowerOfAttorney.EXECUTION_EXECUTED
            and poa.status == PowerOfAttorney.STATUS_ACTIVE
            and poa.verified_by_user_id
            and poa.activation_workflow_event_id
        ),
        sh4_complete=(
            not package.physical_share_security_required_flag
            or bool(
                sh4
                and sh4.form_status == SH4ShareTransferForm.STATUS_HELD_IN_CUSTODY
                and sh4.custodian_user_id
                and sh4.custody_workflow_event_id
            )
        ),
        cdsl_pledge_complete=(
            not package.demat_pledge_required_flag
            or bool(
                cdsl
                and cdsl.prf_status == CDSLSharePledge.PRF_SUBMITTED
                and cdsl.pledge_acceptance_status == CDSLSharePledge.ACCEPTANCE_ACCEPTED
                and cdsl.pledge_status == CDSLSharePledge.STATUS_CREATED
                and cdsl.acceptance_workflow_event_id
            )
        ),
        blank_dated_cheque_received=bool(
            cheque
            and cheque.cheque_status == BlankDatedCheque.STATUS_HELD
            and cheque.custodian_user_id
            and cheque.custody_workflow_event_id
        ),
    )


__all__ = ["SecurityReadinessFacts", "resolve_security_readiness"]
