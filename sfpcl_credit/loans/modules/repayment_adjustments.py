import hashlib
import json
import uuid
from decimal import Decimal, InvalidOperation

from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import (
    BankStatementLine, ManualAllocationApproval, Repayment, RepaymentAllocation,
    RepaymentReversal, RepaymentReversalLedgerEntry,
)


MANUAL_APPROVE_PERMISSION = "finance.repayment.manual_allocation_approve"
REVERSE_PERMISSION = "finance.repayment.reverse"


class RepaymentAdjustmentValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class RepaymentAdjustmentPermissionDenied(Exception):
    pass


class RepaymentAdjustmentNotFound(Exception):
    pass


class RepaymentAdjustmentConflict(Exception):
    pass


def approve_manual_allocation(
    *, actor, repayment_id, payload, idempotency_key, request=None
):
    cleaned = _validate_approval(payload, idempotency_key)
    payload_digest = _digest(
        {
            "repayment_id": str(repayment_id),
            "actor_user_id": str(actor.pk),
            "loan_account_id": str(cleaned["loan_account_id"]),
            "amount": f"{cleaned['amount']:.2f}",
            "reason": cleaned["reason"],
        }
    )
    try:
        return _approve_manual_allocation(
            actor=actor,
            repayment_id=repayment_id,
            cleaned=cleaned,
            payload_digest=payload_digest,
            request=request,
        )
    except IntegrityError as exc:
        retained = ManualAllocationApproval.objects.filter(
            idempotency_key_digest=cleaned["idempotency_key_digest"]
        ).first()
        if retained and retained.payload_digest == payload_digest:
            return _serialize_approval(retained)
        raise RepaymentAdjustmentConflict(
            "The approval idempotency key or repayment is already in use."
        ) from exc


def reverse_repayment(*, actor, repayment_id, payload, idempotency_key, request=None):
    cleaned = _validate_reversal(payload, idempotency_key)
    payload_digest = _digest(
        {
            "repayment_id": str(repayment_id),
            "actor_user_id": str(actor.pk),
            "reason": cleaned["reason"],
        }
    )
    try:
        return _reverse_repayment(
            actor=actor,
            repayment_id=repayment_id,
            cleaned=cleaned,
            payload_digest=payload_digest,
            request=request,
        )
    except IntegrityError as exc:
        retained = RepaymentReversal.objects.filter(
            idempotency_key_digest=cleaned["idempotency_key_digest"]
        ).first()
        if retained and retained.payload_digest == payload_digest:
            return _serialize_reversal(retained)
        raise RepaymentAdjustmentConflict(
            "The reversal idempotency key or repayment is already in use."
        ) from exc


@transaction.atomic
def _reverse_repayment(*, actor, repayment_id, cleaned, payload_digest, request):
    _require_explicit_permission(actor, REVERSE_PERMISSION)
    retained_for_key = RepaymentReversal.objects.select_for_update().filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained_for_key:
        if retained_for_key.payload_digest == payload_digest:
            return _serialize_reversal(retained_for_key)
        raise RepaymentAdjustmentConflict(
            "The reversal idempotency key was used for a different request."
        )
    allocation = (
        RepaymentAllocation.objects.select_for_update()
        .select_related("repayment", "loan_account")
        .filter(repayment_id=repayment_id)
        .first()
    )
    if allocation is None:
        raise RepaymentAdjustmentNotFound
    existing = RepaymentReversal.objects.select_for_update().filter(
        allocation=allocation
    ).first()
    if existing:
        if (
            existing.idempotency_key_digest == cleaned["idempotency_key_digest"]
            and existing.payload_digest == payload_digest
        ):
            return _serialize_reversal(existing)
        raise RepaymentAdjustmentConflict(
            "The repayment was already reversed with a different idempotency key."
        )
    account = allocation.loan_account
    repayment = allocation.repayment
    if not _adjustment_in_scope(actor, account, include_repaid=True):
        raise RepaymentAdjustmentNotFound
    if (
        account.principal_outstanding != allocation.principal_after
        or account.interest_outstanding != allocation.interest_after
        or account.charges_outstanding != allocation.charges_after
        or account.total_outstanding != allocation.total_after
        or account.loan_account_status != allocation.loan_status_after
        or repayment.allocation_status
        not in {"allocated", "allocated_with_exception"}
    ):
        raise RepaymentAdjustmentConflict(
            "The retained account or repayment state is stale for reversal."
        )
    applications = list(
        allocation.schedule_applications.select_for_update()
        .select_related("repayment_schedule")
        .order_by("repayment_schedule__installment_number")
    )
    if not applications:
        raise RepaymentAdjustmentConflict(
            "The retained schedule application evidence is incomplete."
        )
    for application in applications:
        schedule = application.repayment_schedule
        if (
            schedule.paid_principal < application.principal_applied
            or schedule.paid_interest < application.interest_applied
            or schedule.schedule_status != application.schedule_status_after
        ):
            raise RepaymentAdjustmentConflict(
                "The retained schedule state is stale for reversal."
            )
    reversal_id = uuid.uuid4()
    reversed_at = timezone.now()
    restored_total = (
        allocation.allocated_to_principal
        + allocation.allocated_to_interest
        + allocation.allocated_to_charges
    )
    evidence = {
        "repayment_reversal_id": str(reversal_id),
        "repayment_allocation_id": str(allocation.pk),
        "repayment_id": str(repayment.pk),
        "loan_account_id": str(account.pk),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "principal_before": f"{allocation.principal_after:.2f}",
        "principal_after": f"{allocation.principal_before:.2f}",
        "interest_before": f"{allocation.interest_after:.2f}",
        "interest_after": f"{allocation.interest_before:.2f}",
        "total_before": f"{allocation.total_after:.2f}",
        "total_after": f"{allocation.total_before:.2f}",
        "reversal_reason_sha256": hashlib.sha256(
            cleaned["reason"].encode()
        ).hexdigest(),
        "reversed_at": reversed_at.isoformat().replace("+00:00", "Z"),
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    audit = _audit(
        actor=actor,
        action="repayment.reversed",
        entity_id=reversal_id,
        evidence=evidence,
        request=request,
    )
    reversal = RepaymentReversal.objects.create(
        repayment_reversal_id=reversal_id,
        allocation=allocation,
        repayment=repayment,
        loan_account=account,
        reversal_reason=cleaned["reason"],
        principal_restored=allocation.allocated_to_principal,
        interest_restored=allocation.allocated_to_interest,
        charges_restored=allocation.allocated_to_charges,
        total_before=allocation.total_after,
        total_after=allocation.total_before,
        reversed_by_user=actor,
        reversal_audit=audit,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        reversed_at=reversed_at,
    )
    for application in applications:
        schedule = application.repayment_schedule
        schedule.paid_principal -= application.principal_applied
        schedule.paid_interest -= application.interest_applied
        schedule.schedule_status = application.schedule_status_before
        schedule.save(
            update_fields=["paid_principal", "paid_interest", "schedule_status"]
        )
    account.principal_outstanding = allocation.principal_before
    account.interest_outstanding = allocation.interest_before
    account.charges_outstanding = allocation.charges_before
    account.total_outstanding = allocation.total_before
    account.loan_account_status = allocation.loan_status_before
    account.save(
        update_fields=[
            "principal_outstanding",
            "interest_outstanding",
            "charges_outstanding",
            "total_outstanding",
            "loan_account_status",
        ]
    )
    repayment.allocation_status = "reversed"
    repayment.save(update_fields=["allocation_status"])
    RepaymentReversalLedgerEntry.objects.create(
        reversal=reversal,
        loan_account=account,
        transaction_date=reversed_at.date(),
        debit_amount=restored_total,
        principal_balance=allocation.principal_before,
        interest_balance=allocation.interest_before,
        charges_balance=allocation.charges_before,
        total_outstanding=allocation.total_before,
        actor_user=actor,
        actor_display_name=actor.full_name,
        created_at=reversed_at,
    )
    return _serialize_reversal(reversal)


@transaction.atomic
def _approve_manual_allocation(
    *, actor, repayment_id, cleaned, payload_digest, request
):
    _require_explicit_permission(actor, MANUAL_APPROVE_PERMISSION)
    retained = ManualAllocationApproval.objects.select_for_update().filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained:
        if retained.payload_digest == payload_digest:
            return _serialize_approval(retained)
        raise RepaymentAdjustmentConflict(
            "The approval idempotency key was used for a different request."
        )
    repayment = (
        Repayment.objects.select_for_update(of=("self",))
        .select_related("loan_account", "sap_posting_obligation__posting_audit")
        .filter(pk=repayment_id)
        .first()
    )
    if repayment is None:
        raise RepaymentAdjustmentNotFound
    if not _adjustment_in_scope(
        actor, repayment.loan_account, include_repaid=False
    ):
        raise RepaymentAdjustmentNotFound
    line = (
        BankStatementLine.objects.select_for_update(of=("self",))
        .select_related("match_audit")
        .filter(pk=repayment.bank_statement_line_id)
        .first()
    )
    if not _manual_exception_is_coherent(repayment, line):
        raise RepaymentAdjustmentConflict(
            "A coherent manually matched statement exception is required."
        )
    if cleaned["loan_account_id"] != repayment.loan_account_id:
        raise RepaymentAdjustmentConflict(
            "The approval destination does not match the retained repayment."
        )
    if cleaned["amount"] != repayment.amount_received or line.amount != cleaned["amount"]:
        raise RepaymentAdjustmentConflict(
            "The approval amount does not match the retained exception evidence."
        )
    if repayment.allocation_status != "pending" or repayment.sap_posting_status != "posted":
        raise RepaymentAdjustmentConflict(
            "The repayment is not posted and pending manual allocation."
        )
    approval_id = uuid.uuid4()
    approved_at = timezone.now()
    evidence = {
        "manual_allocation_approval_id": str(approval_id),
        "repayment_id": str(repayment.pk),
        "loan_account_id": str(repayment.loan_account_id),
        "bank_statement_line_id": str(line.pk),
        "approved_amount": f"{cleaned['amount']:.2f}",
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "decision": "approved",
        "approval_reason_sha256": hashlib.sha256(
            cleaned["reason"].encode()
        ).hexdigest(),
        "approved_at": approved_at.isoformat().replace("+00:00", "Z"),
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    audit = _audit(
        actor=actor,
        action="repayment.manual_allocation_approved",
        entity_id=approval_id,
        evidence=evidence,
        request=request,
    )
    approval = ManualAllocationApproval.objects.create(
        manual_allocation_approval_id=approval_id,
        repayment=repayment,
        loan_account_id=repayment.loan_account_id,
        bank_statement_line_id=line.pk,
        approved_amount=cleaned["amount"],
        approval_reason=cleaned["reason"],
        approved_by_user=actor,
        approval_audit=audit,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        approved_at=approved_at,
    )
    return _serialize_approval(approval)


def _validate_approval(payload, key):
    allowed = {"loan_account_id", "amount", "reason"}
    errors = {name: "Unknown field." for name in sorted(set(payload) - allowed)}
    try:
        loan_account_id = uuid.UUID(str(payload.get("loan_account_id", "")))
    except (TypeError, ValueError, AttributeError):
        loan_account_id = None
        errors["loan_account_id"] = "Must be a valid loan account UUID."
    try:
        amount = Decimal(str(payload.get("amount", "")))
        if amount <= 0 or amount.as_tuple().exponent < -2:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        amount = None
        errors["amount"] = "Must be a positive decimal with at most two places."
    reason = str(payload.get("reason", "")).strip()
    if not reason or len(reason) > 500:
        errors["reason"] = "Must be nonblank and at most 500 characters."
    key = str(key or "").strip()
    if not key or len(key) > 200:
        errors["idempotency_key"] = "Idempotency-Key is required and must be at most 200 characters."
    if errors:
        raise RepaymentAdjustmentValidation(errors)
    return {
        "loan_account_id": loan_account_id,
        "amount": amount,
        "reason": reason,
        "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
    }


def _validate_reversal(payload, key):
    errors = {name: "Unknown field." for name in sorted(set(payload) - {"reason"})}
    reason = str(payload.get("reason", "")).strip()
    if not reason or len(reason) > 500:
        errors["reason"] = "Must be nonblank and at most 500 characters."
    key = str(key or "").strip()
    if not key or len(key) > 200:
        errors["idempotency_key"] = "Idempotency-Key is required and must be at most 200 characters."
    if errors:
        raise RepaymentAdjustmentValidation(errors)
    return {
        "reason": reason,
        "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
    }


def _manual_exception_is_coherent(repayment, line):
    if line is None or line.match_audit is None:
        return False
    evidence = line.match_audit.new_value_json or {}
    manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return (
        repayment.statement_match_status == "manual_match_exception"
        and line.match_status == "matched"
        and line.matched_repayment_id == repayment.pk
        and line.match_audit.action == "bank_statement.line_manually_matched"
        and line.match_audit.selector_manifest_json == manifest
        and line.match_audit.selector_manifest_sha256
        == hashlib.sha256(manifest.encode()).hexdigest()
        and evidence.get("repayment_id") == str(repayment.pk)
        and evidence.get("loan_account_id") == str(repayment.loan_account_id)
    )


def _require_explicit_permission(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
    ):
        raise RepaymentAdjustmentPermissionDenied


def _adjustment_in_scope(actor, account, *, include_repaid):
    permissions = set(auth_service.effective_permission_codes(actor))
    roles = set(auth_service.effective_role_codes(actor))
    return "finance.repayment.allocate" in permissions and (
        "accounts_head" in roles
        or (
            "credit_manager" in roles
            and account.loan_account_status
            in {
                "active",
                "partially_repaid",
                "overdue",
                "grace_period",
                "extended",
            }
            | ({"repaid"} if include_repaid else set())
        )
    )


def _audit(*, actor, action, entity_id, evidence, request):
    manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="repayment_adjustment",
        entity_id=entity_id,
        old_value_json=None,
        new_value_json=evidence,
        selector_manifest_json=manifest,
        selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _serialize_approval(approval):
    return {
        "manual_allocation_approval_id": str(approval.pk),
        "repayment_id": str(approval.repayment_id),
        "loan_account_id": str(approval.loan_account_id),
        "bank_statement_line_id": str(approval.bank_statement_line_id),
        "approved_amount": f"{approval.approved_amount:.2f}",
        "decision": "approved",
        "approved_at": approval.approved_at.isoformat().replace("+00:00", "Z"),
    }


def _serialize_reversal(reversal):
    return {
        "repayment_reversal_id": str(reversal.pk),
        "repayment_allocation_id": str(reversal.allocation_id),
        "repayment_id": str(reversal.repayment_id),
        "principal_restored": f"{reversal.principal_restored:.2f}",
        "interest_restored": f"{reversal.interest_restored:.2f}",
        "charges_restored": f"{reversal.charges_restored:.2f}",
        "loan_account": {
            "principal_outstanding": f"{reversal.allocation.principal_before:.2f}",
            "interest_outstanding": f"{reversal.allocation.interest_before:.2f}",
            "charges_outstanding": f"{reversal.allocation.charges_before:.2f}",
            "total_outstanding": f"{reversal.total_after:.2f}",
            "status": reversal.allocation.loan_status_before,
        },
    }


__all__ = [
    "RepaymentAdjustmentConflict", "RepaymentAdjustmentNotFound",
    "RepaymentAdjustmentPermissionDenied", "RepaymentAdjustmentValidation",
    "approve_manual_allocation", "reverse_repayment",
]
