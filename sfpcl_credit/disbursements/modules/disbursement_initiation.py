import hashlib
import json
import uuid
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.applications.modules import document_checklist_facts
from sfpcl_credit.communications.models import Notification
from sfpcl_credit.configurations.modules.source_bank_governance import (
    resolve_source_bank_account,
)
from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.disbursements.modules.disbursement_readiness import (
    DisbursementReadinessModule,
    InitiationReadinessDecision,
)
from sfpcl_credit.domain_errors import DomainObjectAccessDenied, DomainPermissionDenied
from sfpcl_credit.identity.models import AuditLog, Permission, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.workflows.events import record_workflow_event


INITIATE_PERMISSION = "finance.disbursement.initiate"


class DisbursementConflict(Exception):
    code = "CONFLICT"


class DisbursementReadinessStale(Exception):
    def __init__(self, message, code="INVALID_STATE_TRANSITION"):
        self.code = code
        super().__init__(message)


def _initiate(*, actor, loan_account_id, payload, idempotency_key, request=None):
    cleaned = _validate_payload(payload, idempotency_key)
    with transaction.atomic():
        maker = _locked_maker(actor)
        payload_digest = _payload_digest(
            loan_account_id=loan_account_id, maker=maker, cleaned=cleaned
        )
        retained = Disbursement.objects.select_for_update().filter(
            idempotency_key_digest=cleaned["idempotency_key_digest"]
        ).first()
        if retained is not None:
            if retained.payload_digest == payload_digest:
                return {
                    "idempotency_replayed": True,
                    "original_response": serialize_disbursement(retained),
                }
            raise DisbursementConflict(
                "The idempotency key is already bound to a different request."
            )
        readiness = DisbursementReadinessModule.evaluate_for_initiation(
            actor=maker, loan_account_id=loan_account_id
        )
        readiness_digest, readiness_evidence = _require_current_readiness(
            readiness, loan_account_id
        )
        account = (
            LoanAccount.objects.select_for_update(of=("self",))
            .select_related("terms", "loan_application", "member", "sanction_decision")
            .filter(pk=loan_account_id)
            .first()
        )
        if account is None:
            raise DomainObjectAccessDenied(None)
        _require_unfunded_account(account, cleaned["disbursement_amount"])
        bank = document_checklist_facts.resolve_blank_cheque_bank_fact(
            application_id=account.loan_application_id
        )
        source = resolve_source_bank_account(for_update=True)
        _require_bank_facts(
            account=account,
            cleaned=cleaned,
            bank=bank,
            source=source,
            readiness_evidence=readiness_evidence,
        )
        if Disbursement.objects.select_for_update().filter(
            loan_account=account,
            authorisation_status__in=("pending", "approved"),
            bank_transfer_status__in=("pending", "processing"),
        ).exists():
            raise DisbursementConflict(
                "An active disbursement initiation already exists for this loan account."
            )

        disbursement_id = uuid.uuid4()
        initiated_at = timezone.now()
        roles = sorted(auth_service.effective_role_codes(maker))
        teams = sorted(maker.team_codes())
        supplied_request_id = request.headers.get("X-Request-ID", "") if request else ""
        request_id = supplied_request_id.strip() or f"req_disbursement_{uuid.uuid4().hex}"
        if len(request_id) > 255:
            request_id = f"req_disbursement_{uuid.uuid4().hex}"
        comment_digest = hashlib.sha256(
            cleaned["final_verification_comments"].encode()
        ).hexdigest()
        trace = (
            f"request_id={request_id};"
            f"verification_digest={comment_digest}"
        )
        safe_evidence = {
            "disbursement_id": str(disbursement_id),
            "loan_account_id": str(account.pk),
            "loan_application_id": str(account.loan_application_id),
            "member_id": str(account.member_id),
            "disbursement_amount": f"{cleaned['disbursement_amount']:.2f}",
            "borrower_bank_account_id": str(cleaned["borrower_bank_account_id"]),
            "source_bank_account_id": str(cleaned["source_bank_account_id"]),
            "maker_user_id": str(maker.pk),
            "maker_role_codes": roles,
            "maker_team_codes": teams,
            "cfc_assignment_role_code": "chief_financial_controller",
            "initiation_status": Disbursement.INITIATED,
            "authorisation_status": Disbursement.AUTHORISATION_PENDING,
            "bank_transfer_status": Disbursement.TRANSFER_PENDING,
            "payment_method": Disbursement.PAYMENT_METHOD_MANUAL,
            "readiness_digest": readiness_digest,
            "readiness_evidence": readiness_evidence,
            "idempotency_digest": cleaned["idempotency_key_digest"],
            "request_id": request_id,
            "final_verification_comment_digest": comment_digest,
            "ip_address": request_ip(request) if request else "",
            "user_agent": request_user_agent(request) if request else "",
            "initiated_at": initiated_at.isoformat().replace("+00:00", "Z"),
            "outcome": "initiated",
        }
        audit = AuditLog.objects.create(
            actor_user=maker,
            actor_type="user",
            action="disbursement.initiated",
            entity_type="disbursement",
            entity_id=disbursement_id,
            old_value_json={},
            new_value_json=safe_evidence,
            ip_address=safe_evidence["ip_address"],
            user_agent=safe_evidence["user_agent"],
        )
        workflow = record_workflow_event(
            actor=maker,
            workflow_name="DisbursementInitiated",
            entity_type="disbursement",
            entity_id=disbursement_id,
            from_state=None,
            to_state=Disbursement.INITIATED,
            trigger_reason=trace,
            action_code="disbursement.initiated",
            metadata=safe_evidence,
        )
        task = Notification.objects.create(
            notification_type="disbursement_authorisation",
            category="Finance",
            severity=Notification.SEVERITY_URGENT,
            title="Disbursement awaiting CFC authorisation",
            message=(
                "A verified manual-bank instruction is awaiting independent review. "
                f"{trace}"
            ),
            related_entity_type="disbursement",
            related_entity_id=disbursement_id,
            action_label="Review disbursement",
            action_url=f"/api/v1/disbursements/{disbursement_id}/authorise/",
            sender_user=maker,
            recipient_role_code="chief_financial_controller",
        )
        try:
            row = Disbursement.objects.create(
                disbursement_id=disbursement_id,
                loan_account=account,
                loan_application_id=account.loan_application_id,
                member_id=account.member_id,
                disbursement_amount=cleaned["disbursement_amount"],
                borrower_bank_account_id=cleaned["borrower_bank_account_id"],
                source_bank_account_id=cleaned["source_bank_account_id"],
                initiated_by_user=maker,
                final_verification_comments=cleaned["final_verification_comments"],
                idempotency_key_digest=cleaned["idempotency_key_digest"],
                payload_digest=payload_digest,
                readiness_digest=readiness_digest,
                readiness_evidence_json=readiness_evidence,
                maker_role_code="senior_manager_finance",
                maker_team_codes_json=teams,
                initiated_at=initiated_at,
                cfc_task=task,
                initiation_audit=audit,
                initiation_workflow_event=workflow,
            )
        except IntegrityError as exc:
            raise DisbursementConflict(
                "A concurrent disbursement initiation already won."
            ) from exc
        return serialize_disbursement(row)


def serialize_disbursement(row):
    return {
        "disbursement_id": str(row.pk),
        "initiation_status": row.initiation_status,
        "authorisation_status": row.authorisation_status,
        "bank_transfer_status": row.bank_transfer_status,
    }


def _validate_payload(payload, idempotency_key):
    allowed = {
        "disbursement_amount",
        "borrower_bank_account_id",
        "source_bank_account_id",
        "final_verification_comments",
    }
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    for field in allowed - set(payload):
        errors[field] = "This field is required."
    try:
        amount = Decimal(str(payload.get("disbursement_amount", "")))
        if not amount.is_finite() or amount.as_tuple().exponent < -2:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        amount = None
        errors["disbursement_amount"] = "Enter a positive amount with at most 2 decimals."
    if amount is not None and (
        amount <= 0 or amount >= Decimal("10000000000000000")
    ):
        errors["disbursement_amount"] = (
            "Amount must be positive and fit the 18,2 money boundary."
        )
    parsed_ids = {}
    for field in ("borrower_bank_account_id", "source_bank_account_id"):
        try:
            parsed_ids[field] = uuid.UUID(str(payload.get(field, "")))
        except (ValueError, TypeError, AttributeError):
            errors[field] = "Must be a valid UUID."
    raw_comments = payload.get("final_verification_comments")
    comments = raw_comments.strip() if isinstance(raw_comments, str) else ""
    if not isinstance(raw_comments, str) or not comments:
        errors["final_verification_comments"] = "This field is required."
    elif len(comments) > 2000:
        errors["final_verification_comments"] = "Must be at most 2000 characters."
    key = idempotency_key.strip() if isinstance(idempotency_key, str) else ""
    if not key or len(key) > 255:
        errors["Idempotency-Key"] = "A valid Idempotency-Key header is required."
    if errors:
        raise ValidationError(errors)
    return {
        "disbursement_amount": amount.quantize(Decimal("0.01")),
        **parsed_ids,
        "final_verification_comments": comments,
        "idempotency_key_digest": hashlib.sha256(key.encode()).hexdigest(),
    }


def _locked_maker(actor):
    maker = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None), status=User.ACTIVE_STATUS)
        .first()
    )
    permissions = set(auth_service.effective_permission_codes(maker)) if maker else set()
    permission = Permission.objects.filter(permission_code=INITIATE_PERMISSION).first()
    if (
        maker is None
        or not maker.can_authenticate()
        or maker.primary_role.status != "active"
        or maker.primary_role.role_code != "senior_manager_finance"
        or INITIATE_PERMISSION not in permissions
        or permission is None
        or permission.risk_level != Permission.RISK_CRITICAL
    ):
        raise DomainPermissionDenied(
            "Active Senior Manager Finance initiation authority is required."
        )
    return maker


def _require_current_readiness(readiness, loan_account_id):
    if not isinstance(readiness, InitiationReadinessDecision):
        raise DisbursementReadinessStale("Current readiness evidence is unavailable.")
    evidence = readiness.safe_evidence()
    if (
        str(readiness.loan_account_id) != str(loan_account_id)
        or readiness.ready_for_disbursement is not True
        or len(readiness.check_digest) != 64
        or any(not value for value in evidence.values())
    ):
        raise DisbursementReadinessStale(
            "All 23 exact current readiness checks must pass in canonical order.",
            readiness.blocker_error_code or "INVALID_STATE_TRANSITION",
        )
    return readiness.check_digest, evidence


def _require_unfunded_account(account, amount):
    zero_fields = (
        account.disbursed_amount,
        account.principal_outstanding,
        account.interest_outstanding,
        account.charges_outstanding,
        account.total_outstanding,
    )
    if (
        account.loan_account_status != LoanAccount.STATUS_SANCTIONED
        or account.loan_application.member_id != account.member_id
        or account.sanction_decision.loan_application_id != account.loan_application_id
        or account.terms.loan_account_id != account.pk
        or any(value != 0 for value in zero_fields)
        or amount != account.terms.loan_amount
        or amount > account.sanctioned_amount
    ):
        raise DisbursementReadinessStale(
            "The loan account amount or unfunded sanctioned state has changed.",
            (
                "DISBURSEMENT_EXCEEDS_SANCTION"
                if amount > account.sanctioned_amount
                or amount != account.terms.loan_amount
                else "INVALID_STATE_TRANSITION"
            ),
        )


def _require_bank_facts(*, account, cleaned, bank, source, readiness_evidence):
    if (
        not bank.valid
        or bank.member_id != account.member_id
        or bank.bank_account_id != cleaned["borrower_bank_account_id"]
        or str(bank.bank_account_id)
        != readiness_evidence["borrower_bank_account_id"]
        or str(bank.bank_verification_decision_id)
        != readiness_evidence["bank_verification_decision_id"]
        or source is None
        or not source.active
        or source.source_bank_account_id != cleaned["source_bank_account_id"]
        or str(source.source_bank_account_id)
        != readiness_evidence["source_bank_account_id"]
        or str(source.governance_id)
        != readiness_evidence["source_bank_governance_id"]
        or str(source.version_history_id)
        != readiness_evidence["source_bank_version_history_id"]
        or str(source.audit_log_id)
        != readiness_evidence["source_bank_audit_log_id"]
    ):
        raise DisbursementReadinessStale(
            "The verified beneficiary or governed source-bank evidence has changed.",
            "BANK_ACCOUNT_NOT_VERIFIED",
        )


def _digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _payload_digest(*, loan_account_id, maker, cleaned):
    return _digest(
        {
            "loan_account_id": str(loan_account_id),
            "actor_user_id": str(maker.pk),
            **{
                key: str(value) if isinstance(value, (uuid.UUID, Decimal)) else value
                for key, value in cleaned.items()
                if key != "idempotency_key_digest"
            },
        }
    )


__all__ = [
    "DisbursementConflict",
    "DisbursementReadinessStale",
]
