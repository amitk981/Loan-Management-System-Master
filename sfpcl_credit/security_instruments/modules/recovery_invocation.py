from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    CDSLSharePledge,
    SH4ShareTransferForm,
)
from sfpcl_credit.workflows.models import WorkflowEvent


class RecoverySecurityUnavailable(Exception):
    pass


def prepare_recovery_invocation(
    *, action_type, loan_application_id, member_id, approval_case_id
):
    if action_type == "invoke_sh4":
        return _usable_sh4(
            loan_application_id=loan_application_id,
            member_id=member_id,
            approval_case_id=approval_case_id,
        )
    if action_type == "invoke_cdsl":
        return _usable_cdsl(
            loan_application_id=loan_application_id,
            member_id=member_id,
            approval_case_id=approval_case_id,
        )
    if action_type == "present_blank_dated_cheque":
        return _usable_cheque(
            loan_application_id=loan_application_id,
            member_id=member_id,
            approval_case_id=approval_case_id,
        )
    raise RecoverySecurityUnavailable("The approved recovery route has no governed security owner.")


def _usable_sh4(*, loan_application_id, member_id, approval_case_id):
    form = (
        SH4ShareTransferForm.objects.select_for_update(of=("self",))
        .select_related("security_package", "shareholding")
        .filter(
            security_package__loan_application_id=loan_application_id,
            member_id=member_id,
        )
        .first()
    )
    event_ok = bool(
        form
        and form.custody_workflow_event_id
        and WorkflowEvent.objects.filter(
            pk=form.custody_workflow_event_id,
            workflow_name="sh4",
            entity_type="sh4_share_transfer_form",
            entity_id=form.pk,
            to_state="held_in_custody",
            triggered_by_user_id=form.custodian_user_id,
            trigger_reason="security.sh4.custodied",
        ).exists()
    )
    if (
        form is None
        or form.form_status != SH4ShareTransferForm.STATUS_HELD_IN_CUSTODY
        or form.returned_at is not None
        or form.invocation_approval_case_id is not None
        or form.custodian_user_id is None
        or not event_ok
        or form.shareholding.member_id != member_id
        or form.shareholding.status != "active"
    ):
        raise RecoverySecurityUnavailable(
            "A matching SH-4 held in governed custody is required."
        )
    return {
        "security_type": "sh4",
        "security_id": str(form.pk),
        "security_package_id": str(form.security_package_id),
        "status": form.form_status,
        "share_count": form.share_count,
        "custody_workflow_event_id": str(form.custody_workflow_event_id),
        "approval_case_id": str(approval_case_id),
    }


def _usable_cdsl(*, loan_application_id, member_id, approval_case_id):
    pledge = (
        CDSLSharePledge.objects.select_for_update(of=("self",))
        .select_related("security_package")
        .filter(
            security_package__loan_application_id=loan_application_id,
            pledgor_member_id=member_id,
        )
        .first()
    )
    event_ok = bool(
        pledge
        and pledge.acceptance_workflow_event_id
        and WorkflowEvent.objects.filter(
            pk=pledge.acceptance_workflow_event_id,
            workflow_name="cdsl_share_pledge",
            entity_type="cdsl_share_pledge",
            entity_id=pledge.pk,
            to_state=CDSLSharePledge.STATUS_CREATED,
            triggered_by_user_id=pledge.verified_by_user_id,
            trigger_reason="security.cdsl_pledge.accepted",
        ).exists()
    )
    if (
        pledge is None
        or pledge.pledge_status != CDSLSharePledge.STATUS_CREATED
        or pledge.pledge_acceptance_status != CDSLSharePledge.ACCEPTANCE_ACCEPTED
        or pledge.invoked_at is not None
        or pledge.unpledged_at is not None
        or pledge.verified_by_user_id is None
        or not event_ok
    ):
        raise RecoverySecurityUnavailable(
            "A matching accepted CDSL pledge is required."
        )
    return {
        "security_type": "cdsl",
        "security_id": str(pledge.pk),
        "security_package_id": str(pledge.security_package_id),
        "status": pledge.pledge_status,
        "pledge_sequence_number_masked": (
            f"********{pledge.pledge_sequence_number[-4:]}"
            if pledge.pledge_sequence_number
            else None
        ),
        "acceptance_workflow_event_id": str(pledge.acceptance_workflow_event_id),
        "approval_case_id": str(approval_case_id),
    }


def _usable_cheque(*, loan_application_id, member_id, approval_case_id):
    cheque = (
        BlankDatedCheque.objects.select_for_update(of=("self",))
        .select_related("security_package")
        .filter(
            security_package__loan_application_id=loan_application_id,
            member_id=member_id,
        )
        .first()
    )
    event_ok = bool(
        cheque
        and cheque.custody_workflow_event_id
        and WorkflowEvent.objects.filter(
            pk=cheque.custody_workflow_event_id,
            workflow_name="blank_dated_cheque",
            entity_type="blank_dated_cheque",
            entity_id=cheque.pk,
            to_state=BlankDatedCheque.STATUS_HELD,
            triggered_by_user_id=cheque.custodian_user_id,
            trigger_reason="security.blank_cheque.custodied",
        ).exists()
    )
    if (
        cheque is None
        or cheque.cheque_status != BlankDatedCheque.STATUS_HELD
        or cheque.returned_at is not None
        or cheque.invocation_approval_case_id is not None
        or cheque.presented_date is not None
        or cheque.amount_presented is not None
        or cheque.custodian_user_id is None
        or not event_ok
    ):
        raise RecoverySecurityUnavailable(
            "A matching blank-dated cheque held in governed custody is required."
        )
    return {
        "security_type": "blank_dated_cheque",
        "security_id": str(cheque.pk),
        "security_package_id": str(cheque.security_package_id),
        "status": cheque.cheque_status,
        "cheque_number_masked": "******",
        "custody_workflow_event_id": str(cheque.custody_workflow_event_id),
        "approval_case_id": str(approval_case_id),
    }
