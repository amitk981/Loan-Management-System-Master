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


TRACER_PERMISSION_CODE = "tracer.lifecycle.run"


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


def create_member(user, request, display_name):
    name = str(display_name or "").strip()
    if not name:
        raise ValidationError("Member display name is required.")
    with transaction.atomic():
        member = Member.objects.create(
            reference=_next_reference(Member, "MEM", "member_id"),
            display_name=name,
            status="active",
        )
        event = _record_event("tracer", "member", member.member_id, None, member.status, user)
        _record_audit(request, user, "tracer.member.created", "member", member.member_id, None, member_payload(member))
        return member, event


def create_application(user, request, member_id, amount):
    amount = positive_amount(amount)
    with transaction.atomic():
        member = Member.objects.select_for_update().get(member_id=member_id)
        application = LoanApplication.objects.create(
            reference=_next_reference(LoanApplication, "APP", "loan_application_id"),
            member=member,
            status="draft",
            amount=amount,
        )
        event = _record_event(
            "tracer",
            "loan_application",
            application.loan_application_id,
            None,
            application.status,
            user,
        )
        _record_audit(
            request,
            user,
            "tracer.loan_application.created",
            "loan_application",
            application.loan_application_id,
            None,
            application_payload(application),
        )
        return application, event


def sanction_application(user, request, application_id):
    with transaction.atomic():
        application = LoanApplication.objects.select_for_update().get(
            loan_application_id=application_id
        )
        _require_status(application.status, "draft")
        previous = application.status
        application.status = "sanctioned"
        application.updated_at = timezone.now()
        application.save(update_fields=["status", "updated_at"])
        event = _record_event(
            "tracer",
            "loan_application",
            application.loan_application_id,
            previous,
            application.status,
            user,
        )
        _record_audit(
            request,
            user,
            "tracer.loan_application.sanctioned",
            "loan_application",
            application.loan_application_id,
            {"status": previous},
            application_payload(application),
        )
        return application, previous, event


def create_loan_account(user, request, application_id):
    with transaction.atomic():
        application = (
            LoanApplication.objects.select_for_update()
            .select_related("member")
            .get(loan_application_id=application_id)
        )
        _require_status(application.status, "sanctioned")
        account = LoanAccount.objects.create(
            reference=_next_reference(LoanAccount, "LAC", "loan_account_id"),
            member=application.member,
            application=application,
            status="pending_disbursement",
            amount=application.amount,
        )
        event = _record_event(
            "tracer",
            "loan_account",
            account.loan_account_id,
            None,
            account.status,
            user,
        )
        _record_audit(
            request,
            user,
            "tracer.loan_account.created",
            "loan_account",
            account.loan_account_id,
            None,
            loan_account_payload(account),
        )
        return account, event


def mark_disbursed(user, request, account_id):
    with transaction.atomic():
        account = LoanAccount.objects.select_for_update().get(loan_account_id=account_id)
        _require_status(account.status, "pending_disbursement")
        previous = account.status
        account.status = "active"
        account.updated_at = timezone.now()
        account.save(update_fields=["status", "updated_at"])
        event = _record_event(
            "tracer", "loan_account", account.loan_account_id, previous, account.status, user
        )
        _record_audit(
            request,
            user,
            "tracer.loan_account.disbursed",
            "loan_account",
            account.loan_account_id,
            {"status": previous},
            loan_account_payload(account),
        )
        return account, previous, event


def post_repayment(user, request, account_id, amount):
    amount = positive_amount(amount)
    with transaction.atomic():
        account = LoanAccount.objects.select_for_update().get(loan_account_id=account_id)
        _require_status(account.status, "active")
        repayment = Repayment.objects.create(
            reference=_next_reference(Repayment, "REP", "repayment_id"),
            loan_account=account,
            amount=amount,
            status="posted",
        )
        event = _record_event(
            "tracer",
            "repayment",
            repayment.repayment_id,
            None,
            repayment.status,
            user,
        )
        _record_audit(
            request,
            user,
            "tracer.repayment.posted",
            "repayment",
            repayment.repayment_id,
            None,
            repayment_payload(repayment),
        )
        return repayment, event


def close_loan(user, request, account_id):
    with transaction.atomic():
        account = LoanAccount.objects.select_for_update().get(loan_account_id=account_id)
        _require_status(account.status, "active")
        if not account.repayments.exists():
            raise TransitionError("Loan account needs one posted repayment before closure.")
        previous = account.status
        account.status = "closed"
        account.updated_at = timezone.now()
        account.save(update_fields=["status", "updated_at"])
        event = _record_event(
            "tracer", "loan_account", account.loan_account_id, previous, account.status, user
        )
        _record_audit(
            request,
            user,
            "tracer.loan_account.closed",
            "loan_account",
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


def _require_status(actual, expected):
    if actual != expected:
        raise TransitionError(f"Expected status {expected}, found {actual}.")


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
