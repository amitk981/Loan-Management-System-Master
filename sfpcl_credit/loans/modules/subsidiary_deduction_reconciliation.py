import hashlib
import json
import unicodedata
import uuid
from decimal import Decimal, InvalidOperation

from django.apps import apps
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.selectors import (
    current_loan_term_document_for_update,
)
from sfpcl_credit.loans.models import (
    BankStatementLine,
    LoanAccount,
    Repayment,
    RepaymentSapPostingObligation,
    SubsidiaryDeductionEvidence,
)
from sfpcl_credit.loans.modules.direct_repayment_posting import (
    RepaymentConflict,
    RepaymentNotFound,
    RepaymentPermissionDenied,
    RepaymentValidation,
)


CREATE_PERMISSION = "finance.repayment.create"
VERIFY_PERMISSION = "finance.repayment.allocate"
CREATE_ROLES = {"credit_manager", "accounts_head"}
SERVICEABLE_STATUSES = {"active", "partially_repaid", "overdue", "grace_period", "extended"}


def capture_subsidiary_deduction(
    *, actor, loan_account_id, payload, idempotency_key, request=None
):
    cleaned = _validate_capture(payload, idempotency_key)
    payload_digest = _digest(
        {
            "loan_account_id": str(loan_account_id),
            "actor_id": str(actor.pk),
            **cleaned["digest_payload"],
        }
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
        raise RepaymentConflict(
            "The idempotency key, deduction reference, or transfer reference is already in use."
        ) from exc


@transaction.atomic
def _capture(*, actor, loan_account_id, cleaned, payload_digest, request):
    _require_authority(actor)
    retained = Repayment.objects.select_for_update().filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained is not None:
        if retained.payload_digest == payload_digest:
            return _replay(retained)
        raise RepaymentConflict(
            "The idempotency key was already used for a different request."
        )
    account = LoanAccount.objects.select_for_update().filter(pk=loan_account_id).first()
    if account is None or not _in_scope(actor, account):
        raise RepaymentNotFound
    retained = Repayment.objects.filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained is not None:
        if retained.payload_digest == payload_digest:
            return _replay(retained)
        raise RepaymentConflict(
            "The idempotency key was already used for a different request."
        )
    if account.loan_account_status not in SERVICEABLE_STATUSES or account.disbursed_amount <= 0:
        raise RepaymentConflict(
            "The loan is not serviceable for subsidiary deduction capture."
        )
    agreement = current_loan_term_document_for_update(
        application_id=account.loan_application_id,
        document_type="tri_party_agreement",
    )
    if agreement is None:
        raise RepaymentConflict(
            "A current verified tri-party agreement is required before capture."
        )
    if Repayment.objects.filter(
        bank_reference_number_normalized=cleaned["transfer_reference_normalized"]
    ).exists():
        raise RepaymentConflict("The transfer reference has already been captured.")

    repayment_id = uuid.uuid4()
    evidence_payload = {
        "repayment_id": str(repayment_id),
        "loan_account_id": str(account.pk),
        "member_id": str(account.member_id),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "amount_received": f"{cleaned['amount_received']:.2f}",
        "received_date": cleaned["received_date"].isoformat(),
        "repayment_source": "subsidiary_deduction",
        "payment_method": "subsidiary_transfer",
        "allocation_status": "pending",
        "sap_posting_status": "pending",
        "tri_party_agreement_id": str(agreement.loan_document_id),
        "subsidiary_company_id": str(cleaned["subsidiary_company_id"]),
        "produce_payment_reference_sha256": hashlib.sha256(
            cleaned["produce_payment_reference_normalized"].encode()
        ).hexdigest(),
        "transfer_reference_sha256": hashlib.sha256(
            cleaned["transfer_reference_normalized"].encode()
        ).hexdigest(),
        "reconciliation_status": "pending_statement",
        "treasury_verification_status": "pending",
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    audit = _audit(actor, repayment_id, evidence_payload, request)
    repayment = Repayment.objects.create(
        repayment_id=repayment_id,
        loan_account=account,
        member_id=account.member_id,
        repayment_source="subsidiary_deduction",
        amount_received=cleaned["amount_received"],
        received_date=cleaned["received_date"],
        payment_method="subsidiary_transfer",
        bank_reference_number=cleaned["transfer_reference"],
        bank_reference_number_normalized=cleaned["transfer_reference_normalized"],
        remarks=cleaned["remarks"],
        captured_by_user=actor,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        capture_audit=audit,
    )
    evidence = SubsidiaryDeductionEvidence.objects.create(
        repayment=repayment,
        subsidiary_company_id=cleaned["subsidiary_company_id"],
        produce_payment_reference=cleaned["produce_payment_reference"],
        produce_payment_reference_normalized=cleaned[
            "produce_payment_reference_normalized"
        ],
        transfer_reference=cleaned["transfer_reference"],
        transfer_reference_normalized=cleaned["transfer_reference_normalized"],
        tri_party_agreement_id=agreement.loan_document_id,
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
    Notification = apps.get_model("communications", "Notification")
    task = Notification.objects.create(
        notification_type="subsidiary_repayment_treasury_verification",
        category="Finance",
        severity="urgent",
        title="Subsidiary deduction requires Treasury verification",
        message="Verify the matched subsidiary transfer before recording the SAP receipt.",
        related_entity_type="repayment",
        related_entity_id=repayment.pk,
        action_label="Verify subsidiary deduction",
        action_url=f"/repayments/{repayment.pk}",
        sender_user=actor,
        recipient_role_code="credit_manager",
    )
    RepaymentSapPostingObligation.objects.create(
        repayment=repayment,
        due_date=cleaned["received_date"],
        task=task,
    )
    return _serialize(repayment, evidence)


@transaction.atomic
def verify_treasury_reconciliation(*, actor, repayment_id, payload, request=None):
    _require_authority(actor, permission=VERIFY_PERMISSION)
    remarks = _validate_verification(payload)
    evidence = (
        SubsidiaryDeductionEvidence.objects.select_for_update(of=("self",))
        .select_related("repayment__loan_account")
        .filter(repayment_id=repayment_id)
        .first()
    )
    if evidence is None or not _in_scope(actor, evidence.repayment.loan_account):
        raise RepaymentNotFound
    if evidence.treasury_verification_status == "verified":
        retained = evidence.treasury_verification_audit
        retained_payload = retained.new_value_json if retained else {}
        if (
            retained is None
            or retained_payload.get("actor_user_id") != str(actor.pk)
            or retained_payload.get("remarks_sha256")
            != hashlib.sha256(remarks.encode()).hexdigest()
        ):
            raise RepaymentConflict(
                "Treasury verification is already final for a different request."
            )
        return _serialize(evidence.repayment, evidence)
    if evidence.reconciliation_status == "exception":
        retained = (
            AuditLog.objects.filter(
                action="repayment.subsidiary_exception",
                entity_type="subsidiary_deduction_evidence",
                entity_id=evidence.pk,
            )
            .order_by("-created_at", "-audit_log_id")
            .first()
        )
        retained_payload = retained.new_value_json if retained else {}
        if (
            retained is None
            or retained_payload.get("actor_user_id") != str(actor.pk)
            or retained_payload.get("remarks_sha256")
            != hashlib.sha256(remarks.encode()).hexdigest()
        ):
            raise RepaymentConflict(
                "The reconciliation exception is already final for a different request."
            )
        return _serialize(evidence.repayment, evidence)
    current_agreement = current_loan_term_document_for_update(
        application_id=evidence.repayment.loan_account.loan_application_id,
        document_type="tri_party_agreement",
    )
    if (
        current_agreement is None
        or current_agreement.loan_document_id != evidence.tri_party_agreement_id
    ):
        raise RepaymentConflict("The captured tri-party agreement is no longer current.")
    line = (
        BankStatementLine.objects.select_for_update(of=("self",))
        .filter(matched_repayment_id=repayment_id)
        .first()
    )
    if line is None:
        raise RepaymentConflict(
            "An unambiguous or authorised statement match is required before Treasury verification."
        )
    if line.match_status != "matched" or line.matched_repayment_id != repayment_id:
        raise RepaymentConflict(
            "An unambiguous or authorised statement match is required before Treasury verification."
        )
    if evidence.repayment.amount_received > evidence.repayment.loan_account.total_outstanding:
        evidence.reconciliation_status = "exception"
        evidence.save(update_fields=["reconciliation_status"])
        _decision_audit(
            actor=actor,
            action="repayment.subsidiary_exception",
            evidence=evidence,
            line_id=line.pk,
            remarks=remarks,
            request=request,
        )
        return _serialize(evidence.repayment, evidence)
    audit = _decision_audit(
        actor=actor,
        action="repayment.subsidiary_treasury_verified",
        evidence=evidence,
        line_id=line.pk,
        remarks=remarks,
        request=request,
    )
    evidence.reconciliation_status = "reconciled"
    evidence.treasury_verification_status = "verified"
    evidence.treasury_verified_by_user = actor
    evidence.treasury_verified_at = audit.created_at
    evidence.treasury_verification_audit = audit
    evidence.save(
        update_fields=[
            "reconciliation_status",
            "treasury_verification_status",
            "treasury_verified_by_user",
            "treasury_verified_at",
            "treasury_verification_audit",
        ]
    )
    return _serialize(evidence.repayment, evidence)


def _validate_capture(payload, key):
    allowed = {
        "repayment_source",
        "amount_received",
        "received_date",
        "payment_method",
        "bank_reference_number",
        "subsidiary_company_id",
        "produce_payment_reference",
        "transfer_reference",
        "bank_statement_line_id",
        "remarks",
    }
    errors = {name: "Unknown field." for name in sorted(set(payload) - allowed)}
    if payload.get("repayment_source") != "subsidiary_deduction":
        errors["repayment_source"] = "Must be subsidiary_deduction."
    if payload.get("payment_method") != "subsidiary_transfer":
        errors["payment_method"] = "Must be subsidiary_transfer."
    try:
        amount = Decimal(str(payload.get("amount_received", "")))
        if (
            not amount.is_finite()
            or amount <= 0
            or amount > Decimal("9999999999999999.99")
            or amount.as_tuple().exponent < -2
        ):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        amount = None
        errors["amount_received"] = "Must be a positive decimal with at most two places."
    received_date = parse_date(str(payload.get("received_date", "")))
    if received_date is None:
        errors["received_date"] = "Must be a valid date."
    try:
        subsidiary_company_id = uuid.UUID(str(payload.get("subsidiary_company_id", "")))
    except (TypeError, ValueError, AttributeError):
        subsidiary_company_id = None
        errors["subsidiary_company_id"] = "Must be a valid UUID."
    produce_reference = _bounded_reference(
        payload.get("produce_payment_reference"), 255
    )
    if produce_reference is None:
        errors["produce_payment_reference"] = "Must be nonblank and at most 255 characters."
    transfer_reference = _bounded_reference(payload.get("transfer_reference"), 120)
    bank_reference = _bounded_reference(payload.get("bank_reference_number"), 120)
    if transfer_reference is None:
        errors["transfer_reference"] = "Must be nonblank and at most 120 characters."
    if bank_reference is None or (
        transfer_reference is not None
        and _normalize(bank_reference) != _normalize(transfer_reference)
    ):
        errors["bank_reference_number"] = "Must equal the transfer reference."
    raw_line_id = payload.get("bank_statement_line_id")
    try:
        line_id = uuid.UUID(str(raw_line_id)) if raw_line_id not in (None, "") else None
    except (TypeError, ValueError, AttributeError):
        line_id = None
        errors["bank_statement_line_id"] = "Must be a valid UUID."
    remarks = str(payload.get("remarks", "")).strip()
    if not remarks or len(remarks) > 2000:
        errors["remarks"] = "Must be nonblank and at most 2000 characters."
    key = str(key or "").strip()
    if not key or len(key) > 255:
        errors["Idempotency-Key"] = "Must be nonblank and at most 255 characters."
    if errors:
        raise RepaymentValidation(errors)
    digest_payload = {
        "repayment_source": "subsidiary_deduction",
        "amount_received": f"{amount:.2f}",
        "received_date": received_date.isoformat(),
        "payment_method": "subsidiary_transfer",
        "bank_reference_number": transfer_reference,
        "subsidiary_company_id": str(subsidiary_company_id),
        "produce_payment_reference": produce_reference,
        "transfer_reference": transfer_reference,
        "bank_statement_line_id": str(line_id) if line_id else None,
        "remarks": remarks,
    }
    return {
        **digest_payload,
        "amount_received": amount,
        "received_date": received_date,
        "bank_statement_line_id": line_id,
        "subsidiary_company_id": subsidiary_company_id,
        "produce_payment_reference_normalized": _normalize(produce_reference),
        "transfer_reference_normalized": _normalize(transfer_reference),
        "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
        "digest_payload": digest_payload,
    }


def _bounded_reference(value, limit):
    normalized = " ".join(unicodedata.normalize("NFKC", str(value or "")).split())
    return normalized if normalized and len(normalized) <= limit else None


def _normalize(value):
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).split()).upper()


def _require_authority(actor, *, permission=CREATE_PERMISSION):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
        or not set(auth_service.effective_role_codes(actor)).intersection(CREATE_ROLES)
    ):
        raise RepaymentPermissionDenied


def _in_scope(actor, account):
    roles = set(auth_service.effective_role_codes(actor))
    return "accounts_head" in roles or (
        "credit_manager" in roles and account.loan_account_status in SERVICEABLE_STATUSES
    )


def _audit(actor, repayment_id, evidence, request):
    manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="repayment.receipt_created",
        entity_type="repayment",
        entity_id=repayment_id,
        old_value_json=None,
        new_value_json=evidence,
        selector_manifest_json=manifest,
        selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _decision_audit(*, actor, action, evidence, line_id, remarks, request):
    decided_at = timezone.now()
    safe_evidence = {
        "repayment_id": str(evidence.repayment_id),
        "loan_account_id": str(evidence.repayment.loan_account_id),
        "bank_statement_line_id": str(line_id),
        "tri_party_agreement_id": str(evidence.tri_party_agreement_id),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "decision": "verified" if action.endswith("verified") else "excess_exception",
        "remarks_sha256": hashlib.sha256(remarks.encode()).hexdigest(),
        "decided_at": decided_at.isoformat().replace("+00:00", "Z"),
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    manifest = json.dumps(safe_evidence, sort_keys=True, separators=(",", ":"))
    return AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="subsidiary_deduction_evidence",
        entity_id=evidence.pk,
        old_value_json=None,
        new_value_json=safe_evidence,
        selector_manifest_json=manifest,
        selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _validate_verification(payload):
    errors = {name: "Unknown field." for name in sorted(set(payload) - {"remarks"})}
    remarks = str(payload.get("remarks", "")).strip()
    if not remarks or len(remarks) > 2000:
        errors["remarks"] = "Must be nonblank and at most 2000 characters."
    if errors:
        raise RepaymentValidation(errors)
    return remarks


def _serialize(repayment, evidence):
    return {
        "repayment_id": str(repayment.pk),
        "loan_account_id": str(repayment.loan_account_id),
        "repayment_source": repayment.repayment_source,
        "amount_received": f"{repayment.amount_received:.2f}",
        "received_date": repayment.received_date.isoformat(),
        "payment_method": repayment.payment_method,
        "bank_reference_number": repayment.bank_reference_number,
        "subsidiary_company_id": str(evidence.subsidiary_company_id),
        "produce_payment_reference": evidence.produce_payment_reference,
        "transfer_reference": evidence.transfer_reference,
        "tri_party_agreement_id": str(evidence.tri_party_agreement_id),
        "bank_statement_line_id": (
            str(repayment.bank_statement_line_id)
            if repayment.bank_statement_line_id is not None
            else None
        ),
        "reconciliation_status": evidence.reconciliation_status,
        "treasury_verification_status": evidence.treasury_verification_status,
        "allocation_status": repayment.allocation_status,
        "sap_posting_status": repayment.sap_posting_status,
    }


def _replay(repayment):
    return {
        "idempotency_replayed": True,
        "original_response": _serialize(
            repayment, repayment.subsidiary_deduction_evidence
        ),
    }


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
