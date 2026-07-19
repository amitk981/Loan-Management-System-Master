import hashlib
import json
import uuid
import unicodedata
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.apps import apps
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import (
    BankStatementLine,
    LoanAccount,
    Repayment,
    RepaymentSapPostingObligation,
)


CREATE_PERMISSION = "finance.repayment.create"
POST_PERMISSION = "finance.repayment.mark_sap_posted"
CREATE_ROLES = {"credit_manager", "accounts_head"}
SERVICEABLE_STATUSES = {"active", "partially_repaid", "overdue", "grace_period", "extended"}


class RepaymentValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class RepaymentPermissionDenied(Exception):
    pass


class RepaymentNotFound(Exception):
    pass


class RepaymentConflict(Exception):
    pass


def capture_direct_repayment(*, actor, loan_account_id, payload, idempotency_key, request=None):
    cleaned = _validate_capture(payload, idempotency_key)
    payload_digest = _digest(
        {"loan_account_id": str(loan_account_id), "actor_id": str(actor.pk), **cleaned["digest_payload"]}
    )
    try:
        return _capture(
            actor=actor,
            loan_account_id=loan_account_id,
            cleaned=cleaned,
            payload_digest=payload_digest,
            request=request,
        )
    except IntegrityError as exc:
        retained = Repayment.objects.filter(
            idempotency_key_digest=cleaned["idempotency_key_digest"]
        ).first()
        if retained is not None and retained.payload_digest == payload_digest:
            return _replay(retained)
        raise RepaymentConflict("The idempotency key or bank reference is already in use.") from exc


@transaction.atomic
def _capture(*, actor, loan_account_id, cleaned, payload_digest, request):
    _require_authority(actor, CREATE_PERMISSION, CREATE_ROLES)
    retained = Repayment.objects.select_for_update().filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained is not None:
        if retained.payload_digest == payload_digest:
            return _replay(retained)
        raise RepaymentConflict("The idempotency key was already used for a different request.")
    account = LoanAccount.objects.select_for_update().filter(pk=loan_account_id).first()
    if account is None or not _in_scope(actor, account):
        raise RepaymentNotFound
    retained = Repayment.objects.filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained is not None:
        if retained.payload_digest == payload_digest:
            return _replay(retained)
        raise RepaymentConflict("The idempotency key was already used for a different request.")
    if account.loan_account_status not in SERVICEABLE_STATUSES or account.disbursed_amount <= 0:
        raise RepaymentConflict("The loan is not serviceable for direct repayment capture.")
    if cleaned["bank_statement_line_id"] is not None and not (
        BankStatementLine.objects.select_for_update()
        .filter(pk=cleaned["bank_statement_line_id"])
        .exists()
    ):
        raise RepaymentValidation(
            {"bank_statement_line_id": "Must identify an existing bank statement line."}
        )
    if Repayment.objects.filter(
        bank_reference_number_normalized=cleaned["bank_reference_number_normalized"]
    ).exists():
        raise RepaymentConflict("The bank reference has already been captured.")

    repayment_id = uuid.uuid4()
    created_at = timezone.now()
    safe_evidence = {
        "repayment_id": str(repayment_id),
        "loan_account_id": str(account.pk),
        "member_id": str(account.member_id),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "amount_received": f"{cleaned['amount_received']:.2f}",
        "received_date": cleaned["received_date"].isoformat(),
        "repayment_source": "direct_farmer",
        "payment_method": cleaned["payment_method"],
        "allocation_status": "pending",
        "sap_posting_status": "pending",
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    audit = _audit(
        actor=actor,
        action="repayment.receipt_created",
        entity_type="repayment",
        entity_id=repayment_id,
        evidence=safe_evidence,
        request=request,
    )
    repayment = Repayment.objects.create(
        repayment_id=repayment_id,
        loan_account=account,
        member_id=account.member_id,
        amount_received=cleaned["amount_received"],
        received_date=cleaned["received_date"],
        payment_method=cleaned["payment_method"],
        bank_reference_number=cleaned["bank_reference_number"],
        bank_reference_number_normalized=cleaned["bank_reference_number_normalized"],
        remarks=cleaned["remarks"],
        captured_by_user=actor,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        capture_audit=audit,
        created_at=created_at,
    )
    if cleaned["bank_statement_line_id"] is not None:
        from sfpcl_credit.loans.modules.bank_statement_matching import (
            BankStatementConflict,
            BankStatementNotFound,
            BankStatementPermissionDenied,
            BankStatementValidation,
            claim_statement_line_for_direct_capture,
        )

        try:
            claim_statement_line_for_direct_capture(
                actor=actor,
                line_id=cleaned["bank_statement_line_id"],
                repayment=repayment,
                request=request,
            )
        except BankStatementPermissionDenied as exc:
            raise RepaymentPermissionDenied from exc
        except BankStatementNotFound as exc:
            raise RepaymentNotFound from exc
        except BankStatementValidation as exc:
            raise RepaymentValidation(exc.field_errors) from exc
        except BankStatementConflict as exc:
            raise RepaymentConflict(str(exc)) from exc
    due_date = _next_working_day(cleaned["received_date"])
    Notification = apps.get_model("communications", "Notification")
    task = Notification.objects.create(
        notification_type="repayment_sap_posting_due",
        category="Finance",
        severity="urgent",
        title="Direct repayment requires SAP posting",
        message=f"Post the confirmed direct repayment in SAP by {due_date.isoformat()}.",
        related_entity_type="repayment",
        related_entity_id=repayment.pk,
        action_label="Record SAP posting",
        action_url=f"/repayments/{repayment.pk}",
        sender_user=actor,
        recipient_role_code="credit_manager",
    )
    obligation = RepaymentSapPostingObligation.objects.create(
        repayment=repayment, due_date=due_date, task=task
    )
    return _serialize(repayment, obligation)


@transaction.atomic
def mark_sap_posted(*, actor, repayment_id, payload, request=None):
    _require_authority(actor, POST_PERMISSION, CREATE_ROLES)
    cleaned = _validate_posting(payload)
    obligation = (
        RepaymentSapPostingObligation.objects.select_for_update()
        .select_related("repayment", "repayment__loan_account")
        .filter(repayment_id=repayment_id)
        .first()
    )
    if obligation is None or not _in_scope(actor, obligation.repayment.loan_account):
        raise RepaymentNotFound
    if obligation.status != "pending":
        raise RepaymentConflict("The repayment SAP posting is already final.")
    evidence = {
        "repayment_id": str(obligation.repayment_id),
        "obligation_id": str(obligation.pk),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "sap_posting_status": "posted",
        "sap_posted_at": cleaned["sap_posted_at"].isoformat().replace("+00:00", "Z"),
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    audit = _audit(
        actor=actor,
        action="repayment.sap_posted",
        entity_type="repayment",
        entity_id=obligation.repayment_id,
        evidence=evidence,
        request=request,
    )
    obligation.status = "posted"
    obligation.sap_entry_reference = cleaned["sap_entry_reference"]
    obligation.posted_by_user = actor
    obligation.posted_at = cleaned["sap_posted_at"]
    obligation.posting_audit = audit
    obligation.save(
        update_fields=["status", "sap_entry_reference", "posted_by_user", "posted_at", "posting_audit"]
    )
    Repayment.objects.filter(pk=repayment_id).update(sap_posting_status="posted")
    obligation.repayment.sap_posting_status = "posted"
    return _serialize(obligation.repayment, obligation)


def _require_authority(actor, permission, roles):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
        or not set(auth_service.effective_role_codes(actor)).intersection(roles)
    ):
        raise RepaymentPermissionDenied


def _in_scope(actor, account):
    roles = set(auth_service.effective_role_codes(actor))
    return "accounts_head" in roles or (
        "credit_manager" in roles and account.loan_account_status in SERVICEABLE_STATUSES
    )


def _validate_capture(payload, key):
    allowed = {
        "repayment_source", "amount_received", "received_date", "payment_method",
        "bank_reference_number", "bank_statement_line_id", "remarks",
    }
    errors = {name: "Unknown field." for name in sorted(set(payload) - allowed)}
    if payload.get("repayment_source") != "direct_farmer":
        errors["repayment_source"] = "Must be direct_farmer."
    try:
        amount = Decimal(str(payload.get("amount_received", "")))
        if amount <= 0 or amount.as_tuple().exponent < -2 or len(amount.as_tuple().digits) > 18:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        amount = None
        errors["amount_received"] = "Must be a positive decimal with at most two places."
    received_date = parse_date(str(payload.get("received_date", "")))
    if received_date is None:
        errors["received_date"] = "Must be a valid date."
    method = str(payload.get("payment_method", "")).strip().lower()
    if method not in {"rtgs", "neft"}:
        errors["payment_method"] = "Must be rtgs or neft."
    reference = " ".join(
        unicodedata.normalize(
            "NFKC", str(payload.get("bank_reference_number", ""))
        ).split()
    )
    if not reference or len(reference) > 120:
        errors["bank_reference_number"] = "Must be nonblank and at most 120 characters."
    remarks = str(payload.get("remarks", "")).strip()
    if not remarks or len(remarks) > 2000:
        errors["remarks"] = "Must be nonblank and at most 2000 characters."
    raw_line_id = payload.get("bank_statement_line_id")
    try:
        line_id = uuid.UUID(str(raw_line_id)) if raw_line_id not in (None, "") else None
    except (ValueError, TypeError, AttributeError):
        line_id = None
        errors["bank_statement_line_id"] = "Must be a valid UUID."
    key = str(key or "").strip()
    if not key or len(key) > 255:
        errors["Idempotency-Key"] = "Must be nonblank and at most 255 characters."
    if errors:
        raise RepaymentValidation(errors)
    digest_payload = {
        "repayment_source": "direct_farmer", "amount_received": f"{amount:.2f}",
        "received_date": received_date.isoformat(), "payment_method": method,
        "bank_reference_number": reference, "bank_statement_line_id": str(line_id) if line_id else None,
        "remarks": remarks,
    }
    return {
        **digest_payload,
        "amount_received": amount,
        "received_date": received_date,
        "bank_statement_line_id": line_id,
        "bank_reference_number_normalized": reference.upper(),
        "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
        "digest_payload": digest_payload,
    }


def _validate_posting(payload):
    allowed = {"sap_entry_reference", "sap_posted_at", "remarks"}
    errors = {name: "Unknown field." for name in sorted(set(payload) - allowed)}
    reference = str(payload.get("sap_entry_reference", "")).strip()
    if not reference or len(reference) > 120:
        errors["sap_entry_reference"] = "Must be nonblank and at most 120 characters."
    posted_at = parse_datetime(str(payload.get("sap_posted_at", "")))
    if posted_at is None or timezone.is_naive(posted_at):
        errors["sap_posted_at"] = "Must be a timezone-aware timestamp."
    if errors:
        raise RepaymentValidation(errors)
    return {"sap_entry_reference": reference, "sap_posted_at": posted_at}


def _next_working_day(received_date):
    due = received_date + timedelta(days=1)
    while due.weekday() >= 5:
        due += timedelta(days=1)
    return due


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _audit(*, actor, action, entity_type, entity_id, evidence, request):
    manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return AuditLog.objects.create(
        actor_user=actor, actor_type="user", action=action, entity_type=entity_type,
        entity_id=entity_id, old_value_json=None, new_value_json=evidence,
        selector_manifest_json=manifest,
        selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _serialize(repayment, obligation):
    return {
        "repayment_id": str(repayment.pk),
        "loan_account_id": str(repayment.loan_account_id),
        "repayment_source": repayment.repayment_source,
        "amount_received": f"{repayment.amount_received:.2f}",
        "received_date": repayment.received_date.isoformat(),
        "payment_method": repayment.payment_method,
        "bank_reference_number": repayment.bank_reference_number,
        "bank_statement_line_id": (
            str(repayment.bank_statement_line_id)
            if repayment.bank_statement_line_id
            else None
        ),
        "statement_match_status": repayment.statement_match_status,
        "allocation_status": repayment.allocation_status,
        "sap_posting": {
            "status": obligation.status,
            "due_date": obligation.due_date.isoformat(),
            "sap_entry_reference": obligation.sap_entry_reference,
            "posted_at": obligation.posted_at.isoformat().replace("+00:00", "Z") if obligation.posted_at else None,
        },
    }


def _replay(repayment):
    return {"idempotency_replayed": True, "original_response": _serialize(repayment, repayment.sap_posting_obligation)}
