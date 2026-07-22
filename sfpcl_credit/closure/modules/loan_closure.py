"""Canonical closure-readiness and financial-close owner."""

import hashlib
import json
import uuid
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.closure.models import ClosureRequirement, LoanClosure
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory
from sfpcl_credit.shared.audit_text import UnsafeAuditText, safe_audit_text
from sfpcl_credit.workflows.events import record_workflow_event


READ_PERMISSION = "closure.readiness.read"
CLOSE_PERMISSION = "closure.loan.close"
READ_ROLES = {"credit_manager", "company_secretary", "internal_auditor"}


class ClosurePermissionDenied(Exception):
    pass


class ClosureNotFound(Exception):
    pass


class ClosureValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class ClosureConflict(Exception):
    pass


def _scoped_account(*, actor, loan_account_id):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or READ_PERMISSION not in permissions
        or not roles.intersection(READ_ROLES)
    ):
        raise ClosurePermissionDenied
    account = (
        LoanAccount.objects.select_related("loan_application")
        .filter(pk=loan_account_id)
        .first()
    )
    if account is None:
        raise ClosureNotFound
    in_scope = bool(
        "credit_manager" in roles
        and account.loan_account_status
        in {
            "active",
            "partially_repaid",
            "repaid",
            "overdue",
            "grace_period",
            "extended",
            "non_recoverable_under_review",
            "under_recovery",
            "closed",
        }
    )
    in_scope = in_scope or bool(
        "company_secretary" in roles
        and account.loan_application.application_status
        == account.loan_application.STATUS_APPROVED_BY_SANCTION
    )
    if "internal_auditor" in roles:
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        in_scope = in_scope or ApprovalCaseReadScopeGrant.objects.filter(
            role__role_code="internal_auditor",
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        ).exists()
    if not in_scope:
        raise ClosureNotFound
    return account


def _check(code, passed, **details):
    return {"code": code, "status": "pass" if passed else "fail", **details}


def _ledger_is_reconciled(account):
    from sfpcl_credit.loans.models import (
        Repayment,
        RepaymentSapPostingObligation,
        StatementLinkMigrationException,
        SubsidiaryDeductionEvidence,
    )

    repayment_ids = Repayment.objects.filter(loan_account=account).values("pk")
    return not (
        Repayment.objects.filter(
            loan_account=account,
            allocation_status__in=("pending", "allocated_with_exception"),
        ).exists()
        or RepaymentSapPostingObligation.objects.filter(
            repayment__loan_account=account, status="pending"
        ).exists()
        or StatementLinkMigrationException.objects.filter(
            repayment_id__in=repayment_ids, resolution_status="unresolved"
        ).exists()
        or SubsidiaryDeductionEvidence.objects.filter(repayment_id__in=repayment_ids)
        .exclude(reconciliation_status="reconciled", treasury_verification_status="verified")
        .exists()
        or account.total_outstanding
        != account.principal_outstanding
        + account.interest_outstanding
        + account.charges_outstanding
    )


def _security_requirements(account):
    from sfpcl_credit.security_instruments.models import SecurityPackage

    package = SecurityPackage.objects.filter(
        loan_application_id=account.loan_application_id
    ).first()
    if package is None:
        return {
            "security_return_required": False,
            "physical_share_return_required": False,
            "demat_unpledge_required": False,
            "blank_cheque_return_required": False,
            "poa_release_required": False,
        }
    required = bool(
        package.physical_share_security_required_flag
        or package.demat_pledge_required_flag
        or package.blank_cheque_required_flag
        or package.poa_required_flag
    )
    return {
        "security_return_required": required,
        "physical_share_return_required": package.physical_share_security_required_flag,
        "demat_unpledge_required": package.demat_pledge_required_flag,
        "blank_cheque_return_required": package.blank_cheque_required_flag,
        "poa_release_required": package.poa_required_flag,
    }


def _readiness_for_account(account):
    total = (
        account.principal_outstanding
        + account.interest_outstanding
        + account.charges_outstanding
    )
    ledger_reconciled = _ledger_is_reconciled(account)
    pending_recovery = bool(
        account.loan_account_status == "under_recovery"
        or account.recovery_actions.filter(action_status="pending").exists()
    )
    security = _security_requirements(account)
    checks = [
        _check("principal_paid", account.principal_outstanding == Decimal("0.00")),
        _check(
            "interest_paid_or_approved_adjustment",
            account.interest_outstanding == Decimal("0.00"),
            approved_adjustment=False,
        ),
        _check("charges_paid", account.charges_outstanding == Decimal("0.00")),
        _check("ledger_reconciled", ledger_reconciled),
        _check("recovery_clear", not pending_recovery),
        _check("security_tasks_identified", True, **security),
    ]
    return {
        "loan_account_id": str(account.pk),
        "ready_for_closure": all(row["status"] == "pass" for row in checks),
        "checks": checks,
        "principal_outstanding": f"{account.principal_outstanding:.2f}",
        "interest_outstanding": f"{account.interest_outstanding:.2f}",
        "charges_outstanding": f"{account.charges_outstanding:.2f}",
        "total_outstanding": f"{total:.2f}",
        "interest_adjustment_applied": False,
        **security,
    }


def evaluate_readiness(*, actor, loan_account_id):
    """Return a fresh, server-derived, non-mutating closure decision."""
    account = _scoped_account(actor=actor, loan_account_id=loan_account_id)
    return _readiness_for_account(account)


def close(*, actor, loan_account_id, payload, idempotency_key, request=None):
    try:
        cleaned = _validate_close(payload, idempotency_key)
        _require_close_authority(actor)
    except ClosureValidation:
        _record_denied(
            actor=actor,
            loan_account_id=loan_account_id,
            reason="request_validation_failed",
            message="Loan closure request validation failed.",
            request=request,
        )
        raise
    except ClosurePermissionDenied:
        _record_denied(
            actor=actor,
            loan_account_id=loan_account_id,
            reason="closure_authority_denied",
            message="Loan closure authority is required.",
            request=request,
        )
        raise
    payload_digest = _digest(
        {
            "loan_account_id": str(loan_account_id),
            "actor_id": str(actor.pk),
            "closure_type": cleaned["closure_type"],
            "closure_notes": cleaned["closure_notes"],
        }
    )
    outcome = _close_locked(
        actor=actor,
        loan_account_id=loan_account_id,
        cleaned=cleaned,
        payload_digest=payload_digest,
        request=request,
    )
    if outcome["kind"] == "denied":
        raise ClosureConflict(outcome["message"])
    if outcome["kind"] == "not_found":
        raise ClosureNotFound
    return outcome["data"]


@transaction.atomic
def _close_locked(*, actor, loan_account_id, cleaned, payload_digest, request):
    retained = LoanClosure.objects.select_for_update().filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained is not None:
        if retained.payload_digest == payload_digest:
            return {"kind": "success", "data": _serialize_close(retained, replay=True)}
        return _record_denied(
            actor=actor,
            loan_account_id=loan_account_id,
            reason="idempotency_key_changed_request",
            message="The idempotency key was already used for a different closure request.",
            request=request,
        )
    account = (
        LoanAccount.objects.select_for_update(of=("self",))
        .select_related("loan_application", "terms")
        .filter(pk=loan_account_id)
        .first()
    )
    if account is None:
        outcome = _record_denied(
            actor=actor,
            loan_account_id=loan_account_id,
            reason="loan_account_scope_denied",
            message="The loan account was not found or is inaccessible.",
            request=request,
        )
        outcome["kind"] = "not_found"
        return outcome
    existing = LoanClosure.objects.filter(loan_account=account).first()
    if existing is not None:
        if (
            existing.idempotency_key_digest == cleaned["idempotency_key_digest"]
            and existing.payload_digest == payload_digest
        ):
            return {"kind": "success", "data": _serialize_close(existing, replay=True)}
        return _record_denied(
            actor=actor,
            loan_account_id=account.pk,
            reason="loan_already_financially_closed",
            message="The loan account has already been financially closed.",
            request=request,
        )
    if not _account_in_close_scope(actor, account):
        outcome = _record_denied(
            actor=actor,
            loan_account_id=loan_account_id,
            reason="loan_account_scope_denied",
            message="The loan account was not found or is inaccessible.",
            request=request,
        )
        outcome["kind"] = "not_found"
        return outcome
    readiness = _readiness_for_account(account)
    if not readiness["ready_for_closure"]:
        failed = [row["code"] for row in readiness["checks"] if row["status"] == "fail"]
        return _record_denied(
            actor=actor,
            loan_account_id=account.pk,
            reason="fresh_readiness_failed",
            message="The loan is not fully repaid or has unresolved closure blockers.",
            request=request,
            details={"failed_checks": failed},
        )
    closure_id = uuid.uuid4()
    closed_at = timezone.now()
    roles = set(auth_service.effective_role_codes(actor))
    close_role = "credit_manager" if "credit_manager" in roles else "company_secretary"
    old_status = account.loan_account_status
    workflow = record_workflow_event(
        actor=actor,
        workflow_name="loan_closure",
        entity_type="loan_closure",
        entity_id=closure_id,
        from_state=old_status,
        to_state=LoanClosure.STAGE_FINANCIALLY_CLOSED,
        trigger_reason="Fresh server-derived closure checks passed.",
        action_code=CLOSE_PERMISSION,
    )
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="closure.loan.financially_closed",
        entity_type="loan_closure",
        entity_id=closure_id,
        old_value_json={
            "loan_account_id": str(account.pk),
            "loan_account_status": old_status,
        },
        new_value_json={
            "loan_account_id": str(account.pk),
            "loan_account_status": "closed",
            "closure_stage": LoanClosure.STAGE_FINANCIALLY_CLOSED,
            "closure_type": cleaned["closure_type"],
            "closed_by_role_code": close_role,
            "readiness_snapshot": readiness,
            "idempotency_key_digest": cleaned["idempotency_key_digest"],
            "request_id": request.headers.get("X-Request-ID", "") if request else "",
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    closure = LoanClosure.objects.create(
        loan_closure_id=closure_id,
        loan_account=account,
        member_id=account.member_id,
        closure_type=cleaned["closure_type"],
        closure_stage=LoanClosure.STAGE_FINANCIALLY_CLOSED,
        closure_notes=cleaned["closure_notes"],
        principal_paid_flag=True,
        interest_paid_flag=True,
        charges_paid_flag=True,
        total_outstanding_at_closure=Decimal("0.00"),
        readiness_snapshot_json=readiness,
        closed_by_user=actor,
        closed_by_role_code=close_role,
        closed_at=closed_at,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        close_audit=audit,
        workflow_event=workflow,
    )
    security_required = readiness["security_return_required"]
    ClosureRequirement.objects.bulk_create(
        [
            ClosureRequirement(
                loan_closure=closure,
                requirement_type=ClosureRequirement.TYPE_NOC,
                requirement_status=ClosureRequirement.STATUS_PENDING,
                applicability_snapshot_json={"required": True},
            ),
            ClosureRequirement(
                loan_closure=closure,
                requirement_type=ClosureRequirement.TYPE_SECURITY_RETURN,
                requirement_status=(
                    ClosureRequirement.STATUS_PENDING
                    if security_required
                    else ClosureRequirement.STATUS_NOT_APPLICABLE
                ),
                applicability_snapshot_json={
                    key: readiness[key]
                    for key in (
                        "security_return_required",
                        "physical_share_return_required",
                        "demat_unpledge_required",
                        "blank_cheque_return_required",
                        "poa_release_required",
                    )
                },
            ),
            ClosureRequirement(
                loan_closure=closure,
                requirement_type=ClosureRequirement.TYPE_ARCHIVE,
                requirement_status=ClosureRequirement.STATUS_PENDING,
                applicability_snapshot_json={"required": True},
            ),
        ]
    )
    LoanStatusHistory.objects.create(
        loan_account=account,
        from_status=old_status,
        to_status="closed",
        reason="Full-repayment financial close; controlled checklist actions remain.",
        changed_by_user=actor,
        changed_at=closed_at,
        loan_application_id_snapshot=account.loan_application_id,
        member_id_snapshot=account.member_id,
        sanction_decision_id_snapshot=account.sanction_decision_id,
        sap_customer_code_id_snapshot=account.sap_customer_code_id,
        loan_terms_id_snapshot=account.terms.pk,
        replay_flag=False,
        outcome="financially_closed",
    )
    account.loan_account_status = "closed"
    account.closed_at = closed_at
    account.save(update_fields=["loan_account_status", "closed_at"])
    return {"kind": "success", "data": _serialize_close(closure, replay=False)}


@transaction.atomic
def _record_denied(*, actor, loan_account_id, reason, message, request, details=None):
    evidence = {"reason": reason, **(details or {})}
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.loan.close_denied",
        entity_type="loan_account",
        entity_id=loan_account_id,
        new_value_json=evidence,
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    record_workflow_event(
        actor=actor,
        workflow_name="loan_closure",
        entity_type="loan_account",
        entity_id=loan_account_id,
        from_state=None,
        to_state="financial_close_denied",
        trigger_reason=reason,
        action_code=CLOSE_PERMISSION,
    )
    return {"kind": "denied", "message": message}


def _require_close_authority(actor):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or CLOSE_PERMISSION not in permissions
        or not roles.intersection({"credit_manager", "company_secretary"})
    ):
        raise ClosurePermissionDenied


def _account_in_close_scope(actor, account):
    roles = set(auth_service.effective_role_codes(actor))
    if account.loan_account_status not in {
        "partially_repaid",
        "repaid",
        "under_recovery",
    }:
        return False
    if "credit_manager" in roles:
        return True
    if (
        "company_secretary" not in roles
        or account.loan_application.application_status
        != account.loan_application.STATUS_APPROVED_BY_SANCTION
    ):
        return False
    from sfpcl_credit.security_instruments.models import SecurityPackage

    return bool(
        SecurityPackage.objects.filter(
            loan_application_id=account.loan_application_id
        ).exists()
        or account.recovery_actions.exists()
        or LoanClosure.objects.filter(loan_account=account).exists()
    )


def _validate_close(payload, idempotency_key):
    allowed = {"closure_type", "closure_notes"}
    errors = {name: "Unknown field; closure readiness is server-derived." for name in sorted(set(payload) - allowed)}
    closure_type = str(payload.get("closure_type", "")).strip()
    if closure_type != LoanClosure.TYPE_FULL_REPAYMENT:
        errors["closure_type"] = "Must be full_repayment."
    try:
        notes = safe_audit_text(payload.get("closure_notes"), max_length=2000)
    except UnsafeAuditText as exc:
        notes = ""
        errors["closure_notes"] = str(exc)
    key = str(idempotency_key or "").strip()
    if not key or len(key) > 255:
        errors["Idempotency-Key"] = "Must be nonblank and at most 255 characters."
    if errors:
        raise ClosureValidation(errors)
    return {
        "closure_type": closure_type,
        "closure_notes": notes,
        "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
    }


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _serialize_close(closure, *, replay):
    requirements = {
        row.requirement_type: row.requirement_status
        for row in closure.requirements.all()
    }
    return {
        "loan_closure_id": str(closure.pk),
        "loan_account_id": str(closure.loan_account_id),
        "loan_account_status": "closed",
        "closure_stage": closure.closure_stage,
        "closure_type": closure.closure_type,
        "closed_at": closure.closed_at.isoformat().replace("+00:00", "Z"),
        "noc_required": requirements.get("noc") == "pending",
        "security_return_required": requirements.get("security_return") == "pending",
        "archive_required": requirements.get("archive") == "pending",
        "requirements": requirements,
        "idempotency_replayed": replay,
        "available_actions": [
            "closure.noc.issue",
            "closure.security_return.record",
            "closure.archive.create",
        ],
    }


class LoanClosureModule:
    evaluate_readiness = staticmethod(evaluate_readiness)
    close = staticmethod(close)
