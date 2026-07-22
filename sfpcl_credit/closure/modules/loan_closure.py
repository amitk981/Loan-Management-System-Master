"""Canonical closure-readiness and financial-close owner."""

import hashlib
import json
import uuid
from datetime import date
from decimal import Decimal
from math import ceil

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.closure.models import (
    ArchiveRecord,
    ClosureRequirement,
    LoanClosure,
    NocRecord,
)
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatchConflict,
    CommunicationDispatcher,
)
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog, PortalAccount, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.object_permissions import evaluate_object_access
from sfpcl_credit.legal_documents.modules.noc_document import (
    resolve_generated_noc_evidence,
)
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory
from sfpcl_credit.shared.audit_text import UnsafeAuditText, safe_audit_text
from sfpcl_credit.workflows.events import record_workflow_event


READ_PERMISSION = "closure.readiness.read"
CLOSE_PERMISSION = "closure.loan.close"
NOC_ISSUE_PERMISSION = "closure.noc.issue"
ARCHIVE_CREATE_PERMISSION = "closure.archive.create"
ARCHIVE_READ_PERMISSION = "closure.archive.read"
READ_ROLES = {"credit_manager", "company_secretary", "internal_auditor"}
NOC_ISSUE_ROLES = {"company_secretary", "compliance_team_member"}
ARCHIVE_CREATE_ROLES = {"company_secretary", "compliance_team_member"}
NOC_TEMPLATE_CODE = "noc_issued_email"


class ClosurePermissionDenied(Exception):
    pass


class ClosureNotFound(Exception):
    pass


class ClosureValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class ClosureConflict(Exception):
    pass


class NocValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class NocConflict(Exception):
    pass


class ArchiveValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class ArchiveConflict(Exception):
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


def archive(*, actor, loan_closure_id, payload, idempotency_key, request=None):
    try:
        cleaned = _validate_archive_request(payload, idempotency_key)
        archive_role = _require_archive_authority(actor)
    except ArchiveValidation:
        _record_archive_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="request_validation_failed",
            request=request,
        )
        raise
    except ClosurePermissionDenied:
        _record_archive_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="archive_authority_denied",
            request=request,
        )
        raise
    payload_digest = _digest(
        {
            "loan_closure_id": str(loan_closure_id),
            "actor_id": str(actor.pk),
            "file_location_physical": cleaned["file_location_physical"],
            "file_location_digital": cleaned["file_location_digital"],
            "retention_start_date": (
                cleaned["retention_start_date"].isoformat()
                if cleaned["retention_start_date"]
                else None
            ),
            "retention_until_date": (
                cleaned["retention_until_date"].isoformat()
                if cleaned["retention_until_date"]
                else None
            ),
        }
    )
    outcome = _archive_locked(
        actor=actor,
        archive_role=archive_role,
        loan_closure_id=loan_closure_id,
        cleaned=cleaned,
        payload_digest=payload_digest,
        request=request,
    )
    if outcome["kind"] == "not_found":
        raise ClosureNotFound
    if outcome["kind"] == "denied":
        raise ArchiveConflict(outcome["message"])
    return outcome["data"]


def read_archive(*, actor, loan_closure_id, request=None):
    record = (
        ArchiveRecord.objects.select_related(
            "loan_closure__loan_account__loan_application"
        )
        .filter(loan_closure_id=loan_closure_id)
        .first()
    )
    access = _archive_read_access(actor=actor, record=record)
    if access != "allowed":
        _record_archive_read_denied(
            actor=actor, loan_closure_id=loan_closure_id, request=request
        )
        if access == "forbidden":
            raise ClosurePermissionDenied
        raise ClosureNotFound
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.archive.manifest_accessed",
        entity_type="archive_record",
        entity_id=record.pk,
        new_value_json={
            "loan_closure_id": str(record.loan_closure_id),
            "loan_account_id": str(record.loan_account_id),
            "request_id": request.headers.get("X-Request-ID", "") if request else "",
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    return _serialize_archive(record, replay=False)


def search_archives(*, actor, query_params, request=None):
    _require_archive_read_authority(actor=actor, request=request)
    allowed = {"search", "page", "page_size"}
    unknown = set(query_params.keys()) - allowed
    if unknown:
        _record_archive_read_denied(
            actor=actor, loan_closure_id=None, request=request
        )
        raise ArchiveValidation(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    search = str(query_params.get("search", "")).strip()
    if len(search) > 200:
        _record_archive_read_denied(
            actor=actor, loan_closure_id=None, request=request
        )
        raise ArchiveValidation({"search": "Must be at most 200 characters."})
    page = _positive_archive_int(query_params.get("page"), 1)
    page_size = min(_positive_archive_int(query_params.get("page_size"), 20), 100)
    queryset = ArchiveRecord.objects.select_related(
        "loan_closure__loan_account__loan_application"
    ).order_by("-archived_at", "-archive_record_id")
    if search:
        queryset = queryset.filter(
            Q(loan_account__loan_account_number__icontains=search)
            | Q(loan_account__member__legal_name__icontains=search)
            | Q(file_location_physical__icontains=search)
            | Q(file_location_digital__icontains=search)
        )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    rows = list(queryset[offset : offset + page_size])
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.archive.manifest_searched",
        entity_type="archive_manifest",
        new_value_json={
            "result_count": len(rows),
            "page": page,
            "page_size": page_size,
            "search_applied": bool(search),
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    return (
        [_serialize_archive(row, replay=False) for row in rows],
        {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    )


@transaction.atomic
def _archive_locked(
    *, actor, archive_role, loan_closure_id, cleaned, payload_digest, request
):
    closure = (
        LoanClosure.objects.select_for_update()
        .select_related("loan_account__loan_application")
        .filter(pk=loan_closure_id)
        .first()
    )
    if closure is None or not _actor_in_archive_scope(actor=actor, closure=closure):
        outcome = _record_archive_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="loan_closure_scope_denied",
            request=request,
            message="The loan closure was not found or is inaccessible.",
        )
        outcome["kind"] = "not_found"
        return outcome
    retained = ArchiveRecord.objects.filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained is not None:
        if (
            retained.loan_closure_id == closure.pk
            and retained.idempotency_key_digest == cleaned["idempotency_key_digest"]
            and retained.payload_digest == payload_digest
        ):
            return {
                "kind": "success",
                "data": _serialize_archive(retained, replay=True),
            }
        return _record_archive_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="archive_already_exists",
            request=request,
            message="The retained archive manifest is read-only.",
        )
    retained = ArchiveRecord.objects.filter(loan_closure=closure).first()
    if retained is not None:
        return _record_archive_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="archive_already_exists",
            request=request,
            message="The retained archive manifest is read-only.",
        )
    requirements = {
        row.requirement_type: row.requirement_status
        for row in closure.requirements.select_for_update()
    }
    eligible = bool(
        closure.closure_type == LoanClosure.TYPE_FULL_REPAYMENT
        and closure.closure_stage == LoanClosure.STAGE_FINANCIALLY_CLOSED
        and closure.loan_account.loan_account_status == "closed"
        and closure.loan_account.closed_at == closure.closed_at
        and NocRecord.objects.filter(loan_closure=closure).exists()
        and requirements.get(ClosureRequirement.TYPE_NOC)
        == ClosureRequirement.STATUS_COMPLETED
        and requirements.get(ClosureRequirement.TYPE_SECURITY_RETURN)
        in {
            ClosureRequirement.STATUS_COMPLETED,
            ClosureRequirement.STATUS_NOT_APPLICABLE,
        }
        and requirements.get(ClosureRequirement.TYPE_ARCHIVE)
        == ClosureRequirement.STATUS_PENDING
    )
    if not eligible:
        return _record_archive_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="archive_prerequisites_incomplete",
            request=request,
            message="Archive requires financial close, NOC, and all applicable security returns.",
        )
    retention_start = closure.closed_at.date()
    minimum_retention = _eight_calendar_years_after(retention_start)
    if cleaned["retention_start_date"] not in {None, retention_start}:
        return _record_archive_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="retention_start_not_closure_date",
            request=request,
            message="Retention starts from the retained financial closure date.",
        )
    supplied_until = cleaned["retention_until_date"]
    if supplied_until is not None and supplied_until < minimum_retention:
        return _record_archive_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="retention_period_too_short",
            request=request,
            message="Archive retention cannot be shorter than eight calendar years.",
        )
    retention_until = supplied_until or minimum_retention
    archive_id = uuid.uuid4()
    archived_at = timezone.now()
    workflow = record_workflow_event(
        actor=actor,
        workflow_name="loan_closure",
        entity_type="archive_record",
        entity_id=archive_id,
        from_state=LoanClosure.STAGE_FINANCIALLY_CLOSED,
        to_state="fully_closed_and_archived",
        trigger_reason="NOC and all applicable security-return prerequisites completed.",
        action_code=ARCHIVE_CREATE_PERMISSION,
    )
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="closure.archive.created",
        entity_type="archive_record",
        entity_id=archive_id,
        old_value_json=None,
        new_value_json={
            "loan_closure_id": str(closure.pk),
            "loan_account_id": str(closure.loan_account_id),
            "retention_start_date": retention_start.isoformat(),
            "retention_until_date": retention_until.isoformat(),
            "physical_location_recorded": bool(cleaned["file_location_physical"]),
            "digital_location_recorded": bool(cleaned["file_location_digital"]),
            "archived_by_role_code": archive_role,
            "request_id": request.headers.get("X-Request-ID", "") if request else "",
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    record = ArchiveRecord.objects.create(
        archive_record_id=archive_id,
        loan_closure=closure,
        loan_account=closure.loan_account,
        file_location_physical=cleaned["file_location_physical"],
        file_location_digital=cleaned["file_location_digital"],
        retention_start_date=retention_start,
        retention_until_date=retention_until,
        archived_by_user=actor,
        archived_by_role_code=archive_role,
        archived_at=archived_at,
        destruction_eligible_flag=False,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        archive_audit=audit,
        archive_workflow_event=workflow,
    )
    if ClosureRequirement.complete_archive_requirement(loan_closure_id=closure.pk) != 1:
        raise IntegrityError("Archive requirement was not in the expected pending state.")
    return {"kind": "success", "data": _serialize_archive(record, replay=False)}


def _validate_archive_request(payload, idempotency_key):
    if not isinstance(payload, dict):
        raise ArchiveValidation({"body": "Expected a JSON object."})
    allowed = {
        "file_location_physical",
        "file_location_digital",
        "retention_start_date",
        "retention_until_date",
    }
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    cleaned = {}
    for field in ("file_location_physical", "file_location_digital"):
        raw_value = payload.get(field)
        if raw_value is not None and not isinstance(raw_value, str):
            errors[field] = "Must be a string."
        value = raw_value.strip() if isinstance(raw_value, str) else ""
        if len(value) > 255:
            errors[field] = "Must be at most 255 characters."
        cleaned[field] = value or None
    if not cleaned["file_location_physical"] and not cleaned["file_location_digital"]:
        errors["file_location"] = "A physical or digital archive location is required."
    for field in ("retention_start_date", "retention_until_date"):
        value = payload.get(field)
        if value in {None, ""}:
            cleaned[field] = None
            continue
        try:
            cleaned[field] = date.fromisoformat(str(value))
        except ValueError:
            errors[field] = "Must be an ISO date."
    key = str(idempotency_key or "").strip()
    if not key or len(key) > 255:
        errors["Idempotency-Key"] = "Must be nonblank and at most 255 characters."
    if errors:
        raise ArchiveValidation(errors)
    cleaned["idempotency_key_digest"] = hashlib.sha256(key.encode()).hexdigest()
    return cleaned


def _eight_calendar_years_after(value):
    try:
        return value.replace(year=value.year + 8)
    except ValueError:
        return value.replace(year=value.year + 8, month=3, day=1)


def _require_archive_authority(actor):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or ARCHIVE_CREATE_PERMISSION not in permissions
        or not roles.intersection(ARCHIVE_CREATE_ROLES)
    ):
        raise ClosurePermissionDenied
    return (
        "company_secretary"
        if "company_secretary" in roles
        else "compliance_team_member"
    )


def _actor_in_archive_scope(*, actor, closure):
    access = evaluate_object_access(
        actor_user_id=actor.pk,
        actor_team_codes=actor.team_codes(),
        actor_permission_codes=auth_service.effective_permission_codes(actor),
        required_permission=ARCHIVE_CREATE_PERMISSION,
        object_team_code="compliance",
    )
    return bool(
        access.allowed
        and closure.loan_account.loan_application.application_status
        == closure.loan_account.loan_application.STATUS_APPROVED_BY_SANCTION
    )


def _archive_read_access(*, actor, record):
    if not actor.can_authenticate():
        return "forbidden"
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if ARCHIVE_READ_PERMISSION not in permissions:
        return "forbidden"
    allowed_roles = {
        "company_secretary",
        "compliance_team_member",
        "internal_auditor",
    }
    if not roles.intersection(allowed_roles):
        return "forbidden"
    if record is None:
        return "not_found"
    if roles.intersection(ARCHIVE_CREATE_ROLES):
        access = evaluate_object_access(
            actor_user_id=actor.pk,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=ARCHIVE_READ_PERMISSION,
            object_team_code="compliance",
        )
        approved = (
            record.loan_closure.loan_account.loan_application.application_status
            == record.loan_closure.loan_account.loan_application.STATUS_APPROVED_BY_SANCTION
        )
        return "allowed" if access.allowed and approved else "not_found"
    from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

    auditor_scope = ApprovalCaseReadScopeGrant.objects.filter(
        role=actor.primary_role,
        scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
    ).exists()
    return "allowed" if auditor_scope else "not_found"


def _require_archive_read_authority(*, actor, request):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or ARCHIVE_READ_PERMISSION not in permissions
        or not roles.intersection(
            {"company_secretary", "compliance_team_member", "internal_auditor"}
        )
    ):
        _record_archive_read_denied(
            actor=actor, loan_closure_id=None, request=request
        )
        raise ClosurePermissionDenied
    if roles.intersection(ARCHIVE_CREATE_ROLES):
        access = evaluate_object_access(
            actor_user_id=actor.pk,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=ARCHIVE_READ_PERMISSION,
            object_team_code="compliance",
        )
        if access.allowed:
            return
    else:
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        if ApprovalCaseReadScopeGrant.objects.filter(
            role=actor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        ).exists():
            return
    _record_archive_read_denied(actor=actor, loan_closure_id=None, request=request)
    raise ClosurePermissionDenied


def _positive_archive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


@transaction.atomic
def _record_archive_denied(
    *, actor, loan_closure_id, reason, request, message=None
):
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.archive.create_denied",
        entity_type="loan_closure",
        entity_id=loan_closure_id,
        new_value_json={"reason": reason},
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    return {
        "kind": "denied",
        "message": message or "Archive creation failed retained eligibility checks.",
    }


@transaction.atomic
def _record_archive_read_denied(*, actor, loan_closure_id, request):
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.archive.read_denied",
        entity_type="loan_closure",
        entity_id=loan_closure_id,
        new_value_json={"reason": "archive_not_found_or_out_of_scope"},
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _serialize_archive(record, *, replay):
    return {
        "archive_record_id": str(record.pk),
        "loan_closure_id": str(record.loan_closure_id),
        "loan_account_id": str(record.loan_account_id),
        "file_location_physical": record.file_location_physical,
        "file_location_digital": record.file_location_digital,
        "retention_start_date": record.retention_start_date.isoformat(),
        "retention_until_date": record.retention_until_date.isoformat(),
        "archived_by_user_id": str(record.archived_by_user_id),
        "archived_by_role_code": record.archived_by_role_code,
        "archived_at": record.archived_at.isoformat().replace("+00:00", "Z"),
        "destruction_eligible": timezone.localdate() >= record.retention_until_date,
        "destruction_certificate_id": None,
        "idempotency_replayed": replay,
        "available_actions": [],
    }


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
            action
            for action, available in (
                ("closure.noc.issue", requirements.get("noc") == "pending"),
                ("closure.security_return.record", requirements.get("security_return") == "pending"),
                ("closure.archive.create", requirements.get("archive") == "pending"),
            )
            if available
        ],
    }


def generate_noc(*, actor, loan_closure_id, payload, idempotency_key, request=None):
    """Issue one retained NOC and hand its notice to the communication dispatcher."""
    try:
        cleaned = _validate_noc_request(payload, idempotency_key)
        issuer_role = _require_noc_authority(actor)
    except NocValidation:
        _record_noc_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="request_validation_failed",
            request=request,
        )
        raise
    except ClosurePermissionDenied:
        _record_noc_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="noc_authority_denied",
            request=request,
        )
        raise
    payload_digest = _digest(
        {
            "loan_closure_id": str(loan_closure_id),
            "actor_id": str(actor.pk),
            "document_id": str(cleaned["document_id"]),
            "delivery_mode": cleaned["delivery_mode"],
            "recipient_email": cleaned["recipient_email"],
            "signatory_user_id": str(cleaned["signatory_user_id"]),
        }
    )
    outcome = _issue_noc_locked(
        actor=actor,
        issuer_role=issuer_role,
        loan_closure_id=loan_closure_id,
        cleaned=cleaned,
        payload_digest=payload_digest,
        request=request,
    )
    if outcome["kind"] == "not_found":
        raise ClosureNotFound
    if outcome["kind"] == "denied":
        raise NocConflict(outcome["message"])
    return outcome["data"]


def read_noc(*, actor, loan_closure_id, request=None):
    noc = (
        NocRecord.objects.select_related(
            "communication_job", "loan_closure", "loan_account__loan_application"
        )
        .filter(loan_closure_id=loan_closure_id)
        .first()
    )
    access = _noc_read_access(actor=actor, noc=noc)
    if access == "forbidden":
        _record_noc_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="noc_read_authority_denied",
            request=request,
        )
        raise ClosurePermissionDenied
    if access != "allowed" or noc is None:
        _record_noc_read_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            request=request,
        )
        raise ClosureNotFound
    return _serialize_noc(noc, replay=False)


def download_noc(*, actor, loan_closure_id, request):
    noc = (
        NocRecord.objects.select_related(
            "loan_closure", "loan_account__loan_application"
        )
        .filter(loan_closure_id=loan_closure_id)
        .first()
    )
    access = _noc_read_access(actor=actor, noc=noc)
    if access == "forbidden":
        _record_noc_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="noc_download_authority_denied",
            request=request,
        )
        raise ClosurePermissionDenied
    if access != "allowed" or noc is None:
        _record_noc_read_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            request=request,
        )
        raise ClosureNotFound
    return document_services.download_document_file(
        actor, request, noc.document_id
    )


@transaction.atomic
def _issue_noc_locked(
    *, actor, issuer_role, loan_closure_id, cleaned, payload_digest, request
):
    closure = (
        LoanClosure.objects.select_for_update()
        .select_related("loan_account__loan_application", "member")
        .filter(pk=loan_closure_id)
        .first()
    )
    if closure is None:
        outcome = _record_noc_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="loan_closure_scope_denied",
            request=request,
        )
        outcome["kind"] = "not_found"
        return outcome
    if not _actor_in_noc_issue_scope(actor=actor, closure=closure):
        outcome = _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="loan_closure_scope_denied",
            request=request,
        )
        outcome["kind"] = "not_found"
        return outcome
    retained = NocRecord.objects.select_for_update().filter(loan_closure=closure).first()
    if retained is not None:
        if (
            retained.idempotency_key_digest == cleaned["idempotency_key_digest"]
            and retained.payload_digest == payload_digest
        ):
            return {"kind": "success", "data": _serialize_noc(retained, replay=True)}
        return _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="noc_already_issued",
            request=request,
            message="A NOC has already been issued for this loan closure.",
        )
    key_replay = NocRecord.objects.select_for_update().filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if key_replay is not None:
        return _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="idempotency_key_changed_request",
            request=request,
            message="The idempotency key is already bound to another NOC request.",
        )
    if not _eligible_noc_closure(closure):
        return _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="closure_not_eligible_for_noc",
            request=request,
            message="NOC issuance requires an eligible full-repayment closure.",
        )
    signatory = User.objects.select_related("primary_role").filter(
        pk=cleaned["signatory_user_id"],
        status=User.ACTIVE_STATUS,
        primary_role__status="active",
        primary_role__role_code="company_secretary",
    ).first()
    if signatory is None:
        return _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="invalid_noc_signatory",
            request=request,
            message="The selected NOC signatory is not an active Company Secretary.",
        )
    canonical_email = (closure.member.email or "").strip().lower()
    if not canonical_email or cleaned["recipient_email"].lower() != canonical_email:
        return _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="recipient_not_canonical_borrower",
            request=request,
            message="Delivery must use the retained borrower email address.",
        )
    canonical_document_facts = {
        "borrower_name": closure.member.legal_name,
        "loan_account_number": closure.loan_account.loan_account_number,
        "application_reference": (
            closure.loan_account.loan_application.application_reference_number
        ),
        "disbursed_amount": closure.loan_account.disbursed_amount,
        "full_repayment_date": closure.closed_at.date().isoformat(),
    }
    document_evidence = resolve_generated_noc_evidence(
        application_id=closure.loan_account.loan_application_id,
        document_id=cleaned["document_id"],
        canonical_facts=canonical_document_facts,
        signatory=signatory,
    )
    if document_evidence is None:
        return _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="invalid_noc_document",
            request=request,
            message="A governed generated NOC document for this closure is required.",
        )

    noc_id = uuid.uuid4()
    try:
        with transaction.atomic():
            queued = CommunicationDispatcher.queue_from_template(
                actor=actor,
                template_code=NOC_TEMPLATE_CODE,
                recipient={
                    "party_type": "member",
                    "party_id": closure.member_id,
                    "address": canonical_email,
                    "channel": "email",
                },
                context={
                    "request": request,
                    "idempotency_key": f"noc:{noc_id}:communication",
                    "merge_data": {
                        "borrower_name": closure.member.legal_name,
                        "loan_account_number": closure.loan_account.loan_account_number,
                    },
                },
                related_entity={"type": "noc", "id": noc_id},
                delivery_idempotency_key=f"noc:{noc_id}:delivery",
            )
    except (CommunicationDispatchConflict, ValidationError) as exc:
        return _record_noc_denied(
            actor=actor,
            loan_closure_id=closure.pk,
            reason="delivery_handoff_failed",
            request=request,
            message="NOC delivery could not be queued with retained provider truth.",
            details={"failure_type": type(exc).__name__},
        )

    workflow = record_workflow_event(
        actor=actor,
        workflow_name="loan_closure",
        entity_type="noc",
        entity_id=noc_id,
        from_state="pending",
        to_state="issued_delivery_queued",
        trigger_reason="Governed NOC document issued and delivery queued.",
        action_code=NOC_ISSUE_PERMISSION,
    )
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="closure.noc.issued",
        entity_type="noc",
        entity_id=noc_id,
        new_value_json={
            "loan_closure_id": str(closure.pk),
            "loan_account_id": str(closure.loan_account_id),
            "member_id": str(closure.member_id),
            "document_id": str(document_evidence.document_id),
            "loan_document_id": str(document_evidence.loan_document_id),
            "generation_audit_id": str(document_evidence.generation_audit_id),
            "document_template_id": str(document_evidence.document_template_id),
            "document_template_version": document_evidence.document_template_version,
            "renderer_contract_version": document_evidence.renderer_contract_version,
            "document_checksum_sha256": (
                document_evidence.renderer_validated_checksum_sha256
            ),
            "merge_values_sha256": document_evidence.merge_values_sha256,
            "issued_by_role_code": issuer_role,
            "signatory_user_id": str(signatory.pk),
            "signatory_role_code": "company_secretary",
            "delivery_mode": "email",
            "delivery_status": "queued",
            "communication_id": str(queued.communication_id),
            "communication_job_id": str(queued.communication_job_id),
            "request_id": request.headers.get("X-Request-ID", "") if request else "",
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    noc = NocRecord.objects.create(
        noc_id=noc_id,
        loan_closure=closure,
        loan_account=closure.loan_account,
        member=closure.member,
        loan_document_id=document_evidence.loan_document_id,
        document_id=document_evidence.document_id,
        generation_audit_id=document_evidence.generation_audit_id,
        document_template_id_snapshot=document_evidence.document_template_id,
        document_template_version_snapshot=document_evidence.document_template_version,
        renderer_contract_version_snapshot=document_evidence.renderer_contract_version,
        document_checksum_sha256_snapshot=(
            document_evidence.renderer_validated_checksum_sha256
        ),
        merge_values_sha256_snapshot=document_evidence.merge_values_sha256,
        issued_by_user=actor,
        issued_by_role_code=issuer_role,
        signatory_user=signatory,
        signatory_role_code="company_secretary",
        signatory_name_snapshot=signatory.full_name,
        delivery_mode=NocRecord.DELIVERY_EMAIL,
        delivery_status=NocRecord.DELIVERY_QUEUED,
        recipient_address=canonical_email,
        communication_id=queued.communication_id,
        communication_job_id=queued.communication_job_id,
        borrower_name_snapshot=closure.member.legal_name,
        loan_account_number_snapshot=closure.loan_account.loan_account_number,
        application_reference_snapshot=(
            closure.loan_account.loan_application.application_reference_number
        ),
        disbursed_amount_snapshot=closure.loan_account.disbursed_amount,
        full_repayment_at_snapshot=closure.closed_at,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        issue_audit=audit,
        issue_workflow_event=workflow,
    )
    if ClosureRequirement.complete_noc_requirement(loan_closure_id=closure.pk) != 1:
        raise IntegrityError("NOC requirement was not in the expected pending state.")
    return {"kind": "success", "data": _serialize_noc(noc, replay=False)}


def _validate_noc_request(payload, idempotency_key):
    allowed = {"document_id", "delivery_mode", "recipient_email", "signatory_user_id"}
    errors = {
        name: "Unknown field; certificate facts are server-derived."
        for name in sorted(set(payload) - allowed)
    }
    cleaned = {}
    for field in ("document_id", "signatory_user_id"):
        try:
            cleaned[field] = uuid.UUID(str(payload.get(field, "")))
        except (ValueError, TypeError, AttributeError):
            errors[field] = "Must be a valid UUID."
    delivery_mode = str(payload.get("delivery_mode", "")).strip().lower()
    if delivery_mode != NocRecord.DELIVERY_EMAIL:
        errors["delivery_mode"] = "Must be email for the configured delivery dispatcher."
    recipient_email = str(payload.get("recipient_email", "")).strip()
    try:
        validate_email(recipient_email)
    except ValidationError:
        errors["recipient_email"] = "Must be a valid email address."
    key = str(idempotency_key or "").strip()
    if not key or len(key) > 255:
        errors["Idempotency-Key"] = "Must be nonblank and at most 255 characters."
    if errors:
        raise NocValidation(errors)
    return {
        **cleaned,
        "delivery_mode": delivery_mode,
        "recipient_email": recipient_email,
        "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
    }


def _require_noc_authority(actor):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or NOC_ISSUE_PERMISSION not in permissions
        or not roles.intersection(NOC_ISSUE_ROLES)
    ):
        raise ClosurePermissionDenied
    return (
        "company_secretary"
        if "company_secretary" in roles
        else "compliance_team_member"
    )


def _noc_read_access(*, actor, noc):
    if not actor.can_authenticate():
        return "forbidden"
    roles = set(auth_service.effective_role_codes(actor))
    if "borrower_portal_user" in roles:
        member_id = (
            PortalAccount.objects.filter(
                user=actor, status=PortalAccount.STATUS_ACTIVE
            )
            .values_list("member_id", flat=True)
            .first()
        )
        return "allowed" if noc is not None and member_id == noc.member_id else "not_found"
    permissions = set(auth_service.effective_permission_codes(actor))
    if noc is None:
        return (
            "not_found"
            if roles.intersection(
                {"credit_manager", "company_secretary", "compliance_team_member", "internal_auditor"}
            )
            else "forbidden"
        )
    application = noc.loan_account.loan_application
    approved = application.application_status == application.STATUS_APPROVED_BY_SANCTION
    if "credit_manager" in roles:
        access = evaluate_object_access(
            actor_user_id=actor.pk,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=READ_PERMISSION,
            object_owner_user_id=noc.loan_closure.closed_by_user_id,
        )
        return "allowed" if access.allowed else "not_found"
    if "company_secretary" in roles:
        access = evaluate_object_access(
            actor_user_id=actor.pk,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=NOC_ISSUE_PERMISSION,
            object_team_code="compliance",
        )
        return "allowed" if approved and access.allowed else "not_found"
    if "compliance_team_member" in roles:
        access = evaluate_object_access(
            actor_user_id=actor.pk,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=NOC_ISSUE_PERMISSION,
            object_team_code="compliance",
        )
        return "allowed" if approved and access.allowed else "not_found"
    if "internal_auditor" in roles:
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        if not ApprovalCaseReadScopeGrant.objects.filter(
            role=actor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        ).exists():
            return "not_found"
        return "allowed" if "documents.loan_document.read" in permissions else "not_found"
    return "forbidden"


def _actor_in_noc_issue_scope(*, actor, closure):
    roles = set(auth_service.effective_role_codes(actor))
    application = closure.loan_account.loan_application
    access = evaluate_object_access(
        actor_user_id=actor.pk,
        actor_team_codes=actor.team_codes(),
        actor_permission_codes=auth_service.effective_permission_codes(actor),
        required_permission=NOC_ISSUE_PERMISSION,
        object_team_code="compliance",
    )
    return bool(
        roles.intersection(NOC_ISSUE_ROLES)
        and access.allowed
        and application.application_status == application.STATUS_APPROVED_BY_SANCTION
        and closure.loan_account.loan_account_status == "closed"
        and closure.loan_account.closed_at == closure.closed_at
    )


def _eligible_noc_closure(closure):
    return bool(
        closure.closure_type == LoanClosure.TYPE_FULL_REPAYMENT
        and closure.closure_stage == LoanClosure.STAGE_FINANCIALLY_CLOSED
        and closure.principal_paid_flag
        and closure.interest_paid_flag
        and closure.charges_paid_flag
        and closure.total_outstanding_at_closure == Decimal("0.00")
        and closure.loan_account.loan_account_status == "closed"
        and closure.loan_account.closed_at == closure.closed_at
        and closure.loan_account.loan_application.application_status
        == closure.loan_account.loan_application.STATUS_APPROVED_BY_SANCTION
        and closure.requirements.filter(
            requirement_type=ClosureRequirement.TYPE_NOC,
            requirement_status=ClosureRequirement.STATUS_PENDING,
        ).exists()
    )


@transaction.atomic
def _record_noc_denied(
    *, actor, loan_closure_id, reason, request, message=None, details=None
):
    evidence = {"reason": reason, **(details or {})}
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.noc.issue_denied",
        entity_type="loan_closure",
        entity_id=loan_closure_id,
        new_value_json=evidence,
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    record_workflow_event(
        actor=actor,
        workflow_name="loan_closure",
        entity_type="loan_closure",
        entity_id=loan_closure_id,
        from_state=None,
        to_state="noc_issue_denied",
        trigger_reason=reason,
        action_code=NOC_ISSUE_PERMISSION,
    )
    return {
        "kind": "denied",
        "message": message or "NOC issuance failed retained eligibility checks.",
    }


@transaction.atomic
def _record_noc_read_denied(*, actor, loan_closure_id, request):
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.noc.read_denied",
        entity_type="loan_closure",
        entity_id=loan_closure_id,
        new_value_json={"reason": "noc_not_found_or_out_of_scope"},
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _serialize_noc(noc, *, replay):
    status = CommunicationDispatcher.delivery_status(job_id=noc.communication_job_id)
    if NocRecord.synchronize_delivery_status(noc_id=noc.pk, delivery_status=status):
        AuditLog.objects.create(
            action="closure.noc.delivery_status_observed",
            entity_type="noc",
            entity_id=noc.pk,
            old_value_json={"delivery_status": noc.delivery_status},
            new_value_json={
                "delivery_status": status,
                "communication_job_id": str(noc.communication_job_id),
            },
        )
        noc.delivery_status = status
    return {
        "noc_id": str(noc.pk),
        "loan_closure_id": str(noc.loan_closure_id),
        "loan_account_id": str(noc.loan_account_id),
        "member_id": str(noc.member_id),
        "document_id": str(noc.document_id),
        "issued_by_user_id": str(noc.issued_by_user_id),
        "issued_at": noc.issued_at.isoformat().replace("+00:00", "Z"),
        "signatory_user_id": str(noc.signatory_user_id),
        "signatory_role_code": noc.signatory_role_code,
        "delivery_mode": noc.delivery_mode,
        "delivery_status": status,
        "communication_id": str(noc.communication_id),
        "communication_job_id": str(noc.communication_job_id),
        "borrower_name": noc.borrower_name_snapshot,
        "loan_account_number": noc.loan_account_number_snapshot,
        "application_reference": noc.application_reference_snapshot,
        "disbursed_amount": f"{noc.disbursed_amount_snapshot:.2f}",
        "full_repayment_at": noc.full_repayment_at_snapshot.isoformat().replace(
            "+00:00", "Z"
        ),
        "idempotency_replayed": replay,
    }


class LoanClosureModule:
    evaluate_readiness = staticmethod(evaluate_readiness)
    close = staticmethod(close)
    generate_noc = staticmethod(generate_noc)
    read_noc = staticmethod(read_noc)
    download_noc = staticmethod(download_noc)
    archive = staticmethod(archive)
    read_archive = staticmethod(read_archive)
    search_archives = staticmethod(search_archives)
