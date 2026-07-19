import hashlib
import json
import unicodedata
import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.disbursements.models import (
    BankTransfer,
    Disbursement,
    DisbursementAdviceIntent,
    InitialLoanPaymentSapPosting,
    LoanRegisterUpdate,
)
from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    resolve_current_disbursement_evidence,
)
from sfpcl_credit.disbursements.modules.disbursement_authorisation import (
    is_current_terminal_authorisation,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.services import resolve_immutable_upload_provenance
from sfpcl_credit.domain_errors import DomainObjectAccessDenied, DomainPermissionDenied
from sfpcl_credit.identity.models import AuditLog, Permission, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory
from sfpcl_credit.workflows.events import record_workflow_event


MARK_SUCCESS_PERMISSION = "finance.disbursement.mark_success"
SUCCESS_ACTION = "disbursement.transfer_succeeded"
_CFC_ROLE = "chief_financial_controller"
_FINANCE_ROLE = "senior_manager_finance"
_FUTURE_TOLERANCE = timedelta(minutes=5)


class DisbursementTransferConflict(Exception):
    code = "CONFLICT"


class DuplicateBankReference(DisbursementTransferConflict):
    code = "DUPLICATE_BANK_REFERENCE"


def _mark_transfer_successful(
    *, actor, disbursement_id, payload, idempotency_key, request=None
):
    cleaned = _validate_payload(payload, idempotency_key)
    with transaction.atomic():
        operator = _locked_operator(actor)
        payload_digest = _payload_digest(disbursement_id, operator.pk, cleaned)
        replay = (
            Disbursement.objects.select_for_update(of=("self",))
            .select_related(
                "loan_account",
                "loan_account__terms",
                "bank_transfer",
                "bank_transfer_evidence_document",
                "transfer_success_actor_user",
                "transfer_success_audit",
                "transfer_success_workflow_event",
                "transfer_success_loan_status_history",
                "register_update",
                "loan_register_update",
                "advice_intent",
                "initial_payment_sap_posting",
            )
            .filter(
                transfer_success_idempotency_key_digest=cleaned[
                    "idempotency_key_digest"
                ]
            )
            .first()
        )
        if replay is not None:
            if (
                replay.pk == disbursement_id
                and replay.transfer_success_payload_digest == payload_digest
                and completed_success_is_coherent(replay)
            ):
                return {
                    "idempotency_replayed": True,
                    "original_response": serialize_transfer_success(replay),
                }
            raise DisbursementTransferConflict(
                "The idempotency key is already bound to a different transfer request."
            )

        row = (
            Disbursement.objects.select_for_update(of=("self",))
            .select_related(
                "loan_account",
                "loan_account__terms",
                "authorisation_audit",
                "authorisation_workflow_event",
            )
            .filter(pk=disbursement_id)
            .first()
        )
        if row is None:
            raise DomainObjectAccessDenied(None)
        _require_operator_scope(operator, row)
        _lock_transfer_relations(row, cleaned["evidence_document_id"])
        if row.bank_transfer_status == "successful":
            raise DisbursementTransferConflict(
                "The disbursement already has a successful bank transfer."
            )
        current = resolve_current_disbursement_evidence(
            disbursement_id=row.pk,
            for_update=True,
            allowed_authorisation_statuses=("approved",),
        )
        if (
            current is None
            or current.authorisation_action_id != row.authorisation_action_id
            or current.authorisation_audit_id != row.authorisation_audit_id
            or current.authorisation_workflow_event_id
            != row.authorisation_workflow_event_id
            or current.authorisation_evidence_digest
            != row.authorisation_evidence_digest
            or current.authorised_by_user_id != row.authorised_by_user_id
            or current.authorised_at != row.authorised_at
        ):
            raise DisbursementTransferConflict(
                "The approved disbursement evidence is stale or incoherent."
            )
        account = row.loan_account
        _require_transferable_account(row, account)
        if cleaned["disbursed_at"] < row.authorised_at:
            raise ValidationError(
                {"disbursed_at": "Must not be before CFC authorisation."}
            )
        evidence = _current_transfer_evidence(
            document_id=cleaned["evidence_document_id"],
            loan_application_id=row.loan_application_id,
            loan_account_id=row.loan_account_id,
        )
        if (
            BankTransfer.objects.select_for_update()
            .filter(
                bank_reference_number_normalized=cleaned["bank_reference_normalized"]
            )
            .exists()
        ):
            raise DuplicateBankReference("The bank reference already exists.")

        action_id = uuid.uuid4()
        bank_transfer_id = uuid.uuid4()
        loan_status_history_id = uuid.uuid4()
        loan_register_update_id = uuid.uuid4()
        advice_intent_id = uuid.uuid4()
        initial_sap_posting_id = uuid.uuid4()
        request_id = _request_id(request)
        ip_address = request_ip(request) if request else ""
        user_agent = request_user_agent(request) if request else ""
        teams = sorted(operator.team_codes())
        role_code = _operator_role(operator, row)
        reference_digest = _sha256(cleaned["bank_reference_normalized"])
        masked_reference = _masked_reference(cleaned["bank_reference_normalized"])
        evidence_digest = _sha256(
            "|".join(
                (
                    str(row.pk),
                    str(row.authorisation_action_id),
                    str(evidence.document.pk),
                    evidence.document.checksum_sha256,
                    reference_digest,
                    cleaned["disbursed_at"].isoformat(),
                    f"{row.disbursement_amount:.2f}",
                    str(loan_register_update_id),
                    str(advice_intent_id),
                    str(initial_sap_posting_id),
                )
            )
        )
        safe_evidence = {
            "action_id": str(action_id),
            "disbursement_id": str(row.pk),
            "loan_account_id": str(row.loan_account_id),
            "loan_application_id": str(row.loan_application_id),
            "member_id": str(row.member_id),
            "disbursement_amount": f"{row.disbursement_amount:.2f}",
            "source_bank_account_id": str(row.source_bank_account_id),
            "destination_bank_account_id": str(row.borrower_bank_account_id),
            "authorisation_action_id": str(row.authorisation_action_id),
            "authorisation_audit_id": str(row.authorisation_audit_id),
            "authorisation_workflow_event_id": str(row.authorisation_workflow_event_id),
            "authorisation_evidence_digest": row.authorisation_evidence_digest,
            "bank_transfer_id": str(bank_transfer_id),
            "loan_status_history_id": str(loan_status_history_id),
            "loan_register_update_id": str(loan_register_update_id),
            "disbursement_advice_communication_id": str(advice_intent_id),
            "initial_loan_payment_sap_posting_id": str(initial_sap_posting_id),
            "bank_reference_digest": reference_digest,
            "bank_reference_masked": masked_reference,
            "bank_transfer_evidence_document_id": str(evidence.document.pk),
            "bank_transfer_evidence_checksum_sha256": evidence.document.checksum_sha256,
            "actor_user_id": str(operator.pk),
            "actor_role_code": role_code,
            "actor_team_codes": teams,
            "request_id": request_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "disbursed_at": cleaned["disbursed_at"].isoformat().replace("+00:00", "Z"),
            "bank_transfer_status": "successful",
            "loan_account_status": "active",
            "outcome": "successful",
        }
        audit = AuditLog.objects.create(
            actor_user=operator,
            actor_type="user",
            action=SUCCESS_ACTION,
            entity_type="disbursement",
            entity_id=row.pk,
            old_value_json={
                "bank_transfer_status": "pending",
                "loan_account_status": "sanctioned",
            },
            new_value_json=safe_evidence,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        trace = (
            f"action_id={action_id};request_id={request_id};"
            f"evidence_digest={evidence_digest};reference_digest={reference_digest}"
        )
        workflow = record_workflow_event(
            actor=operator,
            workflow_name="DisbursementTransferSucceeded",
            entity_type="disbursement",
            entity_id=row.pk,
            from_state="pending",
            to_state="successful",
            trigger_reason=trace,
            action_code=SUCCESS_ACTION,
            metadata=safe_evidence,
        )
        try:
            BankTransfer.objects.create(
                bank_transfer_id=bank_transfer_id,
                disbursement=row,
                loan_account=account,
                related_entity_id=row.pk,
                source_bank_account_id=row.source_bank_account_id,
                destination_bank_account_id=row.borrower_bank_account_id,
                evidence_document=evidence.document,
                amount=row.disbursement_amount,
                bank_reference_number=cleaned["bank_reference_normalized"],
                bank_reference_number_normalized=cleaned["bank_reference_normalized"],
                initiated_at=row.initiated_at,
                completed_at=cleaned["disbursed_at"],
            )
        except IntegrityError as exc:
            raise DuplicateBankReference(
                "The bank reference or disbursement transfer already exists."
            ) from exc

        account.disbursed_amount = row.disbursement_amount
        account.principal_outstanding = row.disbursement_amount
        account.total_outstanding = row.disbursement_amount
        account.interest_outstanding = 0
        account.charges_outstanding = 0
        account.loan_account_status = "active"
        account.tenure_start_date = cleaned["disbursed_at"].date()
        account.save(
            update_fields=[
                "disbursed_amount",
                "principal_outstanding",
                "total_outstanding",
                "interest_outstanding",
                "charges_outstanding",
                "loan_account_status",
                "tenure_start_date",
            ]
        )
        LoanStatusHistory.objects.create(
            loan_status_history_id=loan_status_history_id,
            loan_account=account,
            from_status="sanctioned",
            to_status="active",
            reason="Activated from exact successful manual bank transfer.",
            changed_by_user=operator,
            changed_at=cleaned["disbursed_at"],
            loan_application_id_snapshot=account.loan_application_id,
            member_id_snapshot=account.member_id,
            sanction_decision_id_snapshot=account.sanction_decision_id,
            sap_customer_code_id_snapshot=account.sap_customer_code_id,
            loan_terms_id_snapshot=account.terms.pk,
            replay_flag=False,
            outcome="activated",
        )
        transfer = BankTransfer.objects.get(pk=bank_transfer_id)
        register_update = LoanRegisterUpdate.objects.create(
            loan_register_update_id=loan_register_update_id,
            disbursement=row,
            bank_transfer=transfer,
            loan_account=account,
            loan_application_id=row.loan_application_id,
            member_id=row.member_id,
            amount=row.disbursement_amount,
            bank_reference_digest=reference_digest,
            evidence_document=evidence.document,
            evidence_checksum_sha256=evidence.document.checksum_sha256,
            transfer_action_id=action_id,
            transfer_evidence_digest=evidence_digest,
            transfer_audit=audit,
            transfer_workflow_event=workflow,
            created_at=cleaned["disbursed_at"],
        )
        advice_intent = DisbursementAdviceIntent.objects.create(
            advice_intent_id=advice_intent_id,
            disbursement=row,
            bank_transfer=transfer,
            loan_account=account,
            loan_application_id=row.loan_application_id,
            member_id=row.member_id,
            amount=row.disbursement_amount,
            bank_reference_digest=reference_digest,
            evidence_document=evidence.document,
            evidence_checksum_sha256=evidence.document.checksum_sha256,
            transfer_action_id=action_id,
            transfer_evidence_digest=evidence_digest,
            transfer_audit=audit,
            transfer_workflow_event=workflow,
            created_at=cleaned["disbursed_at"],
        )
        initial_sap_posting = InitialLoanPaymentSapPosting.objects.create(
            initial_loan_payment_sap_posting_id=initial_sap_posting_id,
            disbursement=row,
            bank_transfer=transfer,
            loan_register_update=register_update,
            loan_account=account,
            loan_application_id=row.loan_application_id,
            member_id=row.member_id,
            amount=row.disbursement_amount,
            transfer_action_id=action_id,
            transfer_evidence_digest=evidence_digest,
            posting_status=InitialLoanPaymentSapPosting.STATUS_PENDING,
            created_at=cleaned["disbursed_at"],
        )
        row.bank_transfer_status = "successful"
        row.bank_reference_number = cleaned["bank_reference_normalized"]
        row.disbursed_at = cleaned["disbursed_at"]
        row.bank_transfer_evidence_document = evidence.document
        row.transfer_success_action_id = action_id
        row.transfer_success_actor_user = operator
        row.transfer_success_role_code = role_code
        row.transfer_success_team_codes_json = teams
        row.transfer_success_idempotency_key_digest = cleaned["idempotency_key_digest"]
        row.transfer_success_payload_digest = payload_digest
        row.transfer_success_evidence_digest = evidence_digest
        row.transfer_success_request_id = request_id
        row.transfer_success_ip_address = ip_address
        row.transfer_success_user_agent = user_agent
        row.transfer_success_audit = audit
        row.transfer_success_workflow_event = workflow
        row.transfer_success_loan_status_history_id = loan_status_history_id
        row.loan_register_updated_flag = True
        row.register_update = register_update
        row.save(
            update_fields=[
                "bank_transfer_status",
                "bank_reference_number",
                "disbursed_at",
                "bank_transfer_evidence_document",
                "transfer_success_action_id",
                "transfer_success_actor_user",
                "transfer_success_role_code",
                "transfer_success_team_codes_json",
                "transfer_success_idempotency_key_digest",
                "transfer_success_payload_digest",
                "transfer_success_evidence_digest",
                "transfer_success_request_id",
                "transfer_success_ip_address",
                "transfer_success_user_agent",
                "transfer_success_audit",
                "transfer_success_workflow_event",
                "transfer_success_loan_status_history",
                "loan_register_updated_flag",
                "register_update",
            ]
        )
        row._state.fields_cache["loan_register_update"] = register_update
        row._state.fields_cache["advice_intent"] = advice_intent
        row._state.fields_cache["initial_payment_sap_posting"] = initial_sap_posting
        return serialize_transfer_success(row)


def serialize_transfer_success(row):
    posting = row.initial_payment_sap_posting
    return {
        "disbursement_id": str(row.pk),
        "bank_transfer_status": "successful",
        "loan_account_status": "active",
        "disbursement_advice_communication_id": str(row.advice_intent.pk),
        "initial_payment_sap_posting": {
            "posting_status": posting.posting_status,
            "sap_posting_reference_masked": _masked_reference(
                posting.sap_posting_reference
            ),
        },
    }


def _validate_payload(payload, idempotency_key):
    if not isinstance(payload, dict):
        raise ValidationError({"non_field_errors": "A JSON object is required."})
    allowed = {
        "bank_reference_number",
        "disbursed_at",
        "bank_transfer_evidence_document_id",
    }
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    for field in allowed - set(payload):
        errors[field] = "This field is required."
    reference = payload.get("bank_reference_number")
    normalized = _normalize_reference(reference) if isinstance(reference, str) else ""
    if not normalized:
        errors["bank_reference_number"] = "This field is required."
    elif len(normalized) > 120:
        errors["bank_reference_number"] = "Must be at most 120 characters."
    raw_time = payload.get("disbursed_at")
    parsed_time = parse_datetime(raw_time) if isinstance(raw_time, str) else None
    if parsed_time is None or timezone.is_naive(parsed_time):
        errors["disbursed_at"] = "Must be a timezone-aware ISO-8601 timestamp."
    elif parsed_time > timezone.now() + _FUTURE_TOLERANCE:
        errors["disbursed_at"] = "Must not be materially in the future."
    try:
        document_id = uuid.UUID(str(payload.get("bank_transfer_evidence_document_id")))
    except (TypeError, ValueError, AttributeError):
        document_id = None
        errors["bank_transfer_evidence_document_id"] = "Must be a valid UUID."
    key = idempotency_key.strip() if isinstance(idempotency_key, str) else ""
    if not key:
        errors["idempotency_key"] = "Idempotency-Key header is required."
    elif len(key) > 255:
        errors["idempotency_key"] = "Idempotency-Key must be at most 255 characters."
    if errors:
        raise ValidationError(errors)
    return {
        "bank_reference_normalized": normalized,
        "disbursed_at": parsed_time,
        "evidence_document_id": document_id,
        "idempotency_key_digest": _sha256(key),
    }


def _locked_operator(actor):
    operator = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None), status=User.ACTIVE_STATUS)
        .first()
    )
    permission = Permission.objects.filter(
        permission_code=MARK_SUCCESS_PERMISSION,
        risk_level=Permission.RISK_CRITICAL,
    ).first()
    if (
        operator is None
        or not operator.can_authenticate()
        or operator.primary_role.status != "active"
        or permission is None
        or MARK_SUCCESS_PERMISSION
        not in auth_service.effective_permission_codes(operator)
    ):
        raise DomainPermissionDenied(
            "Active Critical transfer-success authority is required."
        )
    return operator


def _require_operator_scope(operator, row):
    roles = set(auth_service.effective_role_codes(operator))
    cfc_scope = _CFC_ROLE in roles and row.authorised_by_user_id == operator.pk
    finance_scope = _FINANCE_ROLE in roles and row.initiated_by_user_id == operator.pk
    if not (cfc_scope or finance_scope):
        raise DomainObjectAccessDenied(None)


def _operator_role(operator, row):
    roles = set(auth_service.effective_role_codes(operator))
    if _CFC_ROLE in roles and row.authorised_by_user_id == operator.pk:
        return _CFC_ROLE
    return _FINANCE_ROLE


def _lock_transfer_relations(row, document_id):
    from sfpcl_credit.applications.models import LoanApplication
    from sfpcl_credit.members.models import BankAccount, Member
    from sfpcl_credit.workflows.models import WorkflowEvent

    LoanAccount.objects.select_for_update().get(pk=row.loan_account_id)
    LoanApplication.objects.select_for_update().get(pk=row.loan_application_id)
    Member.objects.select_for_update().get(pk=row.member_id)
    list(
        BankAccount.objects.select_for_update()
        .filter(pk__in=(row.borrower_bank_account_id, row.source_bank_account_id))
        .order_by("bank_account_id")
    )
    DocumentFile.objects.select_for_update().filter(pk=document_id).first()
    AuditLog.objects.select_for_update().get(pk=row.authorisation_audit_id)
    WorkflowEvent.objects.select_for_update().get(
        pk=row.authorisation_workflow_event_id
    )


def _require_transferable_account(row, account):
    values = (
        account.disbursed_amount,
        account.principal_outstanding,
        account.interest_outstanding,
        account.charges_outstanding,
        account.total_outstanding,
    )
    if (
        row.authorisation_status != "approved"
        or row.bank_transfer_status != "pending"
        or row.disbursement_amount <= 0
        or row.disbursement_amount > account.sanctioned_amount
        or row.disbursement_amount > account.terms.loan_amount
        or account.loan_account_status != "sanctioned"
        or account.tenure_start_date is not None
        or any(value != 0 for value in values)
        or row.bank_reference_number is not None
        or row.disbursed_at is not None
        or row.bank_transfer_evidence_document_id is not None
        or row.disbursement_advice_communication_id is not None
        or row.loan_register_updated_flag
        or row.register_update_id is not None
        or BankTransfer.objects.filter(disbursement=row).exists()
        or LoanStatusHistory.objects.filter(
            loan_account=account, from_status="sanctioned", to_status="active"
        ).exists()
        or InitialLoanPaymentSapPosting.objects.filter(disbursement=row).exists()
    ):
        raise DisbursementTransferConflict(
            "The approved account is no longer in the exact unfunded transfer state."
        )


def _current_transfer_evidence(*, document_id, loan_application_id, loan_account_id):
    try:
        provenance = resolve_immutable_upload_provenance(document_id=document_id)
    except ValidationError as exc:
        raise ValidationError(
            {
                "bank_transfer_evidence_document_id": (
                    "Document file was not found or is inaccessible."
                )
            }
        ) from exc
    scoped = (
        provenance.document.sensitivity_level == "restricted"
        and provenance.document_category == "finance"
        and provenance.document.checksum_sha256
        and (
            (
                provenance.related_entity_type == "loan_application"
                and provenance.related_entity_id == loan_application_id
            )
            or (
                provenance.related_entity_type == "loan_account"
                and provenance.related_entity_id == loan_account_id
            )
        )
    )
    if not scoped:
        raise ValidationError(
            {
                "bank_transfer_evidence_document_id": (
                    "Document file was not found or is inaccessible."
                )
            }
        )
    return provenance


def completed_success_is_coherent(row):
    try:
        transfer = row.bank_transfer
        register_update = row.loan_register_update
        advice_intent = row.advice_intent
        posting = row.initial_payment_sap_posting
    except (
        BankTransfer.DoesNotExist,
        LoanRegisterUpdate.DoesNotExist,
        DisbursementAdviceIntent.DoesNotExist,
        InitialLoanPaymentSapPosting.DoesNotExist,
    ):
        return False
    account = row.loan_account
    audit = row.transfer_success_audit
    workflow = row.transfer_success_workflow_event
    try:
        evidence = _current_transfer_evidence(
            document_id=row.bank_transfer_evidence_document_id,
            loan_application_id=row.loan_application_id,
            loan_account_id=row.loan_account_id,
        )
    except ValidationError:
        return False
    histories = list(
        LoanStatusHistory.objects.filter(
            loan_account=account, from_status="sanctioned", to_status="active"
        ).order_by("loan_status_history_id")[:2]
    )
    if len(histories) != 1:
        return False
    history = histories[0]
    reference_digest = _sha256(transfer.bank_reference_number_normalized)
    expected_evidence_digest = _sha256(
        "|".join(
            (
                str(row.pk),
                str(row.authorisation_action_id),
                str(evidence.document.pk),
                evidence.document.checksum_sha256,
                reference_digest,
                row.disbursed_at.isoformat(),
                f"{row.disbursement_amount:.2f}",
                str(register_update.pk),
                str(advice_intent.pk),
                str(posting.pk),
            )
        )
    )
    expected = {
        "action_id": str(row.transfer_success_action_id),
        "disbursement_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_application_id": str(row.loan_application_id),
        "member_id": str(row.member_id),
        "disbursement_amount": f"{row.disbursement_amount:.2f}",
        "source_bank_account_id": str(row.source_bank_account_id),
        "destination_bank_account_id": str(row.borrower_bank_account_id),
        "authorisation_action_id": str(row.authorisation_action_id),
        "authorisation_audit_id": str(row.authorisation_audit_id),
        "authorisation_workflow_event_id": str(row.authorisation_workflow_event_id),
        "authorisation_evidence_digest": row.authorisation_evidence_digest,
        "bank_transfer_id": str(transfer.pk),
        "loan_status_history_id": str(history.pk),
        "loan_register_update_id": str(register_update.pk),
        "disbursement_advice_communication_id": str(advice_intent.pk),
        "initial_loan_payment_sap_posting_id": str(posting.pk),
        "bank_reference_digest": reference_digest,
        "bank_reference_masked": _masked_reference(
            transfer.bank_reference_number_normalized
        ),
        "bank_transfer_evidence_document_id": str(evidence.document.pk),
        "bank_transfer_evidence_checksum_sha256": evidence.document.checksum_sha256,
        "actor_user_id": str(row.transfer_success_actor_user_id),
        "actor_role_code": row.transfer_success_role_code,
        "actor_team_codes": row.transfer_success_team_codes_json,
        "request_id": row.transfer_success_request_id,
        "ip_address": row.transfer_success_ip_address,
        "user_agent": row.transfer_success_user_agent,
        "disbursed_at": row.disbursed_at.isoformat().replace("+00:00", "Z"),
        "bank_transfer_status": "successful",
        "loan_account_status": "active",
        "outcome": "successful",
    }
    trace = (
        f"action_id={row.transfer_success_action_id};"
        f"request_id={row.transfer_success_request_id};"
        f"evidence_digest={row.transfer_success_evidence_digest};"
        f"reference_digest={reference_digest}"
    )
    return bool(
        row.bank_transfer_status == "successful"
        and row.authorisation_status == "approved"
        and row.bank_reference_number
        and row.disbursed_at
        and row.bank_transfer_evidence_document_id
        and row.transfer_success_action_id
        and row.transfer_success_actor_user_id
        and row.transfer_success_evidence_digest
        and row.loan_register_updated_flag
        and row.register_update_id == register_update.pk
        and transfer.disbursement_id == row.pk
        and transfer.loan_account_id == row.loan_account_id
        and transfer.related_entity_id == row.pk
        and transfer.transfer_type == "disbursement"
        and transfer.related_entity_type == "disbursement"
        and transfer.bank_reference_number_normalized == row.bank_reference_number
        and transfer.bank_reference_number == row.bank_reference_number
        and transfer.evidence_document_id == row.bank_transfer_evidence_document_id
        and transfer.amount == row.disbursement_amount
        and transfer.source_bank_account_id == row.source_bank_account_id
        and transfer.destination_bank_account_id == row.borrower_bank_account_id
        and transfer.payment_method == "manual"
        and transfer.bank_status == "successful"
        and transfer.initiated_at == row.initiated_at
        and transfer.completed_at == row.disbursed_at
        and register_update.disbursement_id == row.pk
        and register_update.bank_transfer_id == transfer.pk
        and register_update.loan_account_id == row.loan_account_id
        and register_update.loan_application_id == row.loan_application_id
        and register_update.member_id == row.member_id
        and register_update.amount == row.disbursement_amount
        and register_update.bank_reference_digest == reference_digest
        and register_update.evidence_document_id
        == row.bank_transfer_evidence_document_id
        and register_update.evidence_checksum_sha256
        == evidence.document.checksum_sha256
        and register_update.transfer_action_id == row.transfer_success_action_id
        and register_update.transfer_evidence_digest
        == row.transfer_success_evidence_digest
        and register_update.transfer_audit_id == row.transfer_success_audit_id
        and register_update.transfer_workflow_event_id
        == row.transfer_success_workflow_event_id
        and advice_intent.disbursement_id == row.pk
        and advice_intent.bank_transfer_id == transfer.pk
        and advice_intent.loan_account_id == row.loan_account_id
        and advice_intent.loan_application_id == row.loan_application_id
        and advice_intent.member_id == row.member_id
        and advice_intent.amount == row.disbursement_amount
        and advice_intent.bank_reference_digest == reference_digest
        and advice_intent.evidence_document_id == row.bank_transfer_evidence_document_id
        and advice_intent.evidence_checksum_sha256
        == evidence.document.checksum_sha256
        and advice_intent.transfer_action_id == row.transfer_success_action_id
        and advice_intent.transfer_evidence_digest == row.transfer_success_evidence_digest
        and advice_intent.transfer_audit_id == row.transfer_success_audit_id
        and advice_intent.transfer_workflow_event_id
        == row.transfer_success_workflow_event_id
        and advice_intent.delivery_status
        in {
            DisbursementAdviceIntent.DELIVERY_PENDING,
            DisbursementAdviceIntent.DELIVERY_SENT,
        }
        and posting.disbursement_id == row.pk
        and posting.bank_transfer_id == transfer.pk
        and posting.loan_register_update_id == register_update.pk
        and posting.loan_account_id == row.loan_account_id
        and posting.loan_application_id == row.loan_application_id
        and posting.member_id == row.member_id
        and posting.amount == row.disbursement_amount
        and posting.transfer_action_id == row.transfer_success_action_id
        and posting.transfer_evidence_digest == row.transfer_success_evidence_digest
        and posting.posting_status
        in {
            InitialLoanPaymentSapPosting.STATUS_PENDING,
            InitialLoanPaymentSapPosting.STATUS_POSTED,
        }
        and (
            (
                posting.posting_status == InitialLoanPaymentSapPosting.STATUS_PENDING
                and posting.sap_posting_reference is None
                and posting.posted_at is None
            )
            or (
                posting.posting_status == InitialLoanPaymentSapPosting.STATUS_POSTED
                and bool(posting.sap_posting_reference)
                and posting.posted_at is not None
            )
        )
        and posting.created_at == row.disbursed_at
        and account.loan_account_status == "active"
        and account.disbursed_amount == row.disbursement_amount
        and account.principal_outstanding == row.disbursement_amount
        and account.total_outstanding == row.disbursement_amount
        and account.interest_outstanding == 0
        and account.charges_outstanding == 0
        and account.tenure_start_date == row.disbursed_at.date()
        and history.changed_by_user_id == row.transfer_success_actor_user_id
        and row.transfer_success_loan_status_history_id == history.pk
        and history.changed_at == row.disbursed_at
        and history.loan_application_id_snapshot == account.loan_application_id
        and history.member_id_snapshot == account.member_id
        and history.sanction_decision_id_snapshot == account.sanction_decision_id
        and history.sap_customer_code_id_snapshot == account.sap_customer_code_id
        and history.loan_terms_id_snapshot == account.terms.pk
        and history.outcome == "activated"
        and not history.replay_flag
        and row.transfer_success_evidence_digest == expected_evidence_digest
        and is_current_terminal_authorisation(
            row,
            {
                "decision": "approved",
                "comments": row.authorisation_comments or "",
            },
            require_pending_transfer=False,
        )
        and audit.action == SUCCESS_ACTION
        and audit.actor_user_id == row.transfer_success_actor_user_id
        and audit.actor_type == "user"
        and audit.entity_type == "disbursement"
        and audit.entity_id == row.pk
        and audit.old_value_json
        == {
            "bank_transfer_status": "pending",
            "loan_account_status": "sanctioned",
        }
        and audit.new_value_json == expected
        and audit.ip_address == row.transfer_success_ip_address
        and audit.user_agent == row.transfer_success_user_agent
        and workflow.workflow_name == "DisbursementTransferSucceeded"
        and workflow.entity_type == "disbursement"
        and workflow.entity_id == row.pk
        and workflow.from_state == "pending"
        and workflow.to_state == "successful"
        and workflow.triggered_by_user_id == row.transfer_success_actor_user_id
        and workflow.trigger_reason == trace
    )


def _payload_digest(disbursement_id, actor_id, cleaned):
    return _sha256(
        json.dumps(
            {
                "disbursement_id": str(disbursement_id),
                "actor_id": str(actor_id),
                "bank_reference_number": cleaned["bank_reference_normalized"],
                "disbursed_at": cleaned["disbursed_at"].isoformat(),
                "bank_transfer_evidence_document_id": str(
                    cleaned["evidence_document_id"]
                ),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def _normalize_reference(value):
    normalized = unicodedata.normalize("NFKC", value).strip().upper()
    return " ".join(normalized.split())


def _masked_reference(value):
    if not value:
        return None
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * (len(value) - 4) + value[-4:]


def _request_id(request):
    supplied = request.headers.get("X-Request-ID", "").strip() if request else ""
    return (
        supplied
        if supplied and len(supplied) <= 255
        else f"req_transfer_{uuid.uuid4().hex}"
    )


def _sha256(value):
    return hashlib.sha256(value.encode()).hexdigest()


__all__ = [
    "DisbursementTransferConflict",
    "DuplicateBankReference",
    "completed_success_is_coherent",
]
