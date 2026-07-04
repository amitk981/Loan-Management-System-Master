from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.tracer.models import (
    LoanAccount,
    LoanApplication,
    Member,
    Repayment,
    WorkflowEvent,
)
from sfpcl_credit.workflows.guard import (
    TransitionDefinition,
    evaluate_transition,
)


TRACER_PERMISSION_CODE = "tracer.lifecycle.run"
NEW_STATE = "__new__"

TRACER_TRANSITIONS = (
    TransitionDefinition(
        entity_type="member",
        action_code="create_member",
        from_states=frozenset({NEW_STATE}),
        to_state="active",
        required_permission=TRACER_PERMISSION_CODE,
        audit_action="tracer.member.created",
        workflow_name="tracer",
        workflow_label="Tracer member created",
    ),
    TransitionDefinition(
        entity_type="loan_application",
        action_code="create_application",
        from_states=frozenset({NEW_STATE}),
        to_state="draft",
        required_permission=TRACER_PERMISSION_CODE,
        audit_action="tracer.loan_application.created",
        workflow_name="tracer",
        workflow_label="Tracer loan application created",
    ),
    TransitionDefinition(
        entity_type="loan_application",
        action_code="sanction_application",
        from_states=frozenset({"draft"}),
        to_state="sanctioned",
        required_permission=TRACER_PERMISSION_CODE,
        audit_action="tracer.loan_application.sanctioned",
        workflow_name="tracer",
        workflow_label="Tracer loan application sanctioned",
    ),
    TransitionDefinition(
        entity_type="loan_application",
        action_code="create_loan_account",
        from_states=frozenset({"sanctioned"}),
        to_state="pending_disbursement",
        required_permission=TRACER_PERMISSION_CODE,
        audit_action="tracer.loan_account.created",
        workflow_name="tracer",
        workflow_label="Tracer loan account created",
    ),
    TransitionDefinition(
        entity_type="loan_account",
        action_code="mark_disbursed",
        from_states=frozenset({"pending_disbursement"}),
        to_state="active",
        required_permission=TRACER_PERMISSION_CODE,
        audit_action="tracer.loan_account.disbursed",
        workflow_name="tracer",
        workflow_label="Tracer loan account disbursed",
    ),
    TransitionDefinition(
        entity_type="loan_account",
        action_code="post_repayment",
        from_states=frozenset({"active"}),
        to_state="posted",
        required_permission=TRACER_PERMISSION_CODE,
        audit_action="tracer.repayment.posted",
        workflow_name="tracer",
        workflow_label="Tracer repayment posted",
    ),
    TransitionDefinition(
        entity_type="loan_account",
        action_code="close_loan",
        from_states=frozenset({"active"}),
        to_state="closed",
        required_permission=TRACER_PERMISSION_CODE,
        audit_action="tracer.loan_account.closed",
        workflow_name="tracer",
        workflow_label="Tracer loan account closed",
    ),
)


class TransitionError(Exception):
    pass


def positive_amount(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValidationError("Amount must be a valid decimal string.") from exc
    if amount <= Decimal("0"):
        raise ValidationError("Amount must be positive.")
    return amount.quantize(Decimal("0.01"))


def create_member(user, request, display_name, actor_permissions):
    name = str(display_name or "").strip()
    if not name:
        raise ValidationError("Member display name is required.")
    transition = _evaluate_transition("create_member", NEW_STATE, actor_permissions)
    with transaction.atomic():
        member = Member.objects.create(
            reference=_next_reference(Member, "MEM", "member_id"),
            display_name=name,
            status=transition.next_state,
        )
        event = _record_event(
            transition.definition.workflow_name,
            transition.definition.entity_type,
            member.member_id,
            None,
            member.status,
            user,
        )
        _record_audit(
            request,
            user,
            transition.definition.audit_action,
            transition.definition.entity_type,
            member.member_id,
            None,
            member_payload(member),
        )
        return member, event


def create_application(user, request, member_id, amount, actor_permissions):
    amount = positive_amount(amount)
    transition = _evaluate_transition("create_application", NEW_STATE, actor_permissions)
    with transaction.atomic():
        member = Member.objects.select_for_update().get(member_id=member_id)
        application = LoanApplication.objects.create(
            reference=_next_reference(LoanApplication, "APP", "loan_application_id"),
            member=member,
            status=transition.next_state,
            amount=amount,
        )
        event = _record_event(
            transition.definition.workflow_name,
            transition.definition.entity_type,
            application.loan_application_id,
            None,
            application.status,
            user,
        )
        _record_audit(
            request,
            user,
            transition.definition.audit_action,
            transition.definition.entity_type,
            application.loan_application_id,
            None,
            application_payload(application),
        )
        return application, event


def sanction_application(user, request, application_id, actor_permissions):
    with transaction.atomic():
        application = LoanApplication.objects.select_for_update().get(
            loan_application_id=application_id
        )
        transition = _evaluate_transition(
            "sanction_application", application.status, actor_permissions
        )
        previous = transition.previous_state
        application.status = transition.next_state
        application.updated_at = timezone.now()
        application.save(update_fields=["status", "updated_at"])
        event = _record_event(
            transition.definition.workflow_name,
            transition.definition.entity_type,
            application.loan_application_id,
            previous,
            application.status,
            user,
        )
        _record_audit(
            request,
            user,
            transition.definition.audit_action,
            transition.definition.entity_type,
            application.loan_application_id,
            {"status": previous},
            application_payload(application),
        )
        return application, previous, event


def create_loan_account(user, request, application_id, actor_permissions):
    with transaction.atomic():
        application = (
            LoanApplication.objects.select_for_update()
            .select_related("member")
            .get(loan_application_id=application_id)
        )
        transition = _evaluate_transition(
            "create_loan_account", application.status, actor_permissions
        )
        account = LoanAccount.objects.create(
            reference=_next_reference(LoanAccount, "LAC", "loan_account_id"),
            member=application.member,
            application=application,
            status=transition.next_state,
            amount=application.amount,
        )
        event = _record_event(
            transition.definition.workflow_name,
            "loan_account",
            account.loan_account_id,
            None,
            account.status,
            user,
        )
        _record_audit(
            request,
            user,
            transition.definition.audit_action,
            "loan_account",
            account.loan_account_id,
            None,
            loan_account_payload(account),
        )
        return account, event


def mark_disbursed(user, request, account_id, actor_permissions):
    with transaction.atomic():
        account = LoanAccount.objects.select_for_update().get(loan_account_id=account_id)
        transition = _evaluate_transition("mark_disbursed", account.status, actor_permissions)
        previous = transition.previous_state
        account.status = transition.next_state
        account.updated_at = timezone.now()
        account.save(update_fields=["status", "updated_at"])
        event = _record_event(
            transition.definition.workflow_name,
            transition.definition.entity_type,
            account.loan_account_id,
            previous,
            account.status,
            user,
        )
        _record_audit(
            request,
            user,
            transition.definition.audit_action,
            transition.definition.entity_type,
            account.loan_account_id,
            {"status": previous},
            loan_account_payload(account),
        )
        return account, previous, event


def post_repayment(user, request, account_id, amount, actor_permissions):
    amount = positive_amount(amount)
    with transaction.atomic():
        account = LoanAccount.objects.select_for_update().get(loan_account_id=account_id)
        transition = _evaluate_transition("post_repayment", account.status, actor_permissions)
        repayment = Repayment.objects.create(
            reference=_next_reference(Repayment, "REP", "repayment_id"),
            loan_account=account,
            amount=amount,
            status=transition.next_state,
        )
        event = _record_event(
            transition.definition.workflow_name,
            "repayment",
            repayment.repayment_id,
            None,
            repayment.status,
            user,
        )
        _record_audit(
            request,
            user,
            transition.definition.audit_action,
            "repayment",
            repayment.repayment_id,
            None,
            repayment_payload(repayment),
        )
        return repayment, event


def close_loan(user, request, account_id, actor_permissions):
    with transaction.atomic():
        account = LoanAccount.objects.select_for_update().get(loan_account_id=account_id)
        transition = _evaluate_transition("close_loan", account.status, actor_permissions)
        if not account.repayments.exists():
            raise TransitionError("Loan account needs one posted repayment before closure.")
        previous = transition.previous_state
        account.status = transition.next_state
        account.updated_at = timezone.now()
        account.save(update_fields=["status", "updated_at"])
        event = _record_event(
            transition.definition.workflow_name,
            transition.definition.entity_type,
            account.loan_account_id,
            previous,
            account.status,
            user,
        )
        _record_audit(
            request,
            user,
            transition.definition.audit_action,
            transition.definition.entity_type,
            account.loan_account_id,
            {"status": previous},
            loan_account_payload(account),
        )
        return account, previous, event


def member_payload(member):
    return {
        "member_id": str(member.member_id),
        "reference": member.reference,
        "display_name": member.display_name,
        "status": member.status,
    }


def application_payload(application):
    return {
        "loan_application_id": str(application.loan_application_id),
        "reference": application.reference,
        "member_id": str(application.member_id),
        "status": application.status,
        "amount": _money(application.amount),
    }


def loan_account_payload(account):
    return {
        "loan_account_id": str(account.loan_account_id),
        "reference": account.reference,
        "member_id": str(account.member_id),
        "loan_application_id": str(account.application_id),
        "status": account.status,
        "amount": _money(account.amount),
    }


def repayment_payload(repayment):
    return {
        "repayment_id": str(repayment.repayment_id),
        "reference": repayment.reference,
        "loan_account_id": str(repayment.loan_account_id),
        "status": repayment.status,
        "amount": _money(repayment.amount),
    }


def action_payload(entity_type, entity_id, previous_status, new_status, workflow_event):
    return {
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "previous_status": previous_status,
        "new_status": new_status,
        "workflow_event_id": str(workflow_event.workflow_event_id),
        "available_actions": [],
    }


def _evaluate_transition(action_code, current_state, actor_permissions):
    return evaluate_transition(
        current_state=current_state,
        requested_action=action_code,
        actor_permissions=actor_permissions,
        transitions=TRACER_TRANSITIONS,
    )


def _next_reference(model, prefix, pk_name):
    next_number = model.objects.count() + 1
    while True:
        reference = f"{prefix}-{next_number:06d}"
        if not model.objects.filter(reference=reference).exists():
            return reference
        next_number += 1


def _record_event(workflow_name, entity_type, entity_id, from_state, to_state, user):
    return WorkflowEvent.objects.create(
        workflow_name=workflow_name,
        entity_type=entity_type,
        entity_id=entity_id,
        from_state=from_state,
        to_state=to_state,
        triggered_by_user=user,
    )


def _record_audit(request, user, action, entity_type, entity_id, old_value, new_value):
    AuditLog.objects.create(
        actor_user=user,
        actor_type="user",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _money(amount):
    return f"{amount:.2f}"
