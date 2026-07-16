import re
import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.applications.modules import application_authority
from sfpcl_credit.applications.modules.document_checklist_facts import (
    resolve_blank_cheque_bank_fact,
)
from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
)
from sfpcl_credit.finance.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.finance.modules.annexure_i import render_annexure_i
from sfpcl_credit.finance.modules.annexure_storage import EncryptedAnnexureStorage
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext
from sfpcl_credit.workflows.events import record_workflow_event


CREATE_PERMISSION = "finance.sap_request.create"
_PAN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
_AADHAAR = re.compile(r"^[0-9]{12}$")


class SapRequestConflict(Exception):
    pass


def create_request(*, actor, application_id, payload, request, storage=None):
    """Create or replay one canonical manual SAP request and Annexure-I file."""
    values = _parse_payload(payload)
    storage = EncryptedAnnexureStorage(storage or LocalDocumentStorage())
    stored_file = None
    try:
        with transaction.atomic():
            actor = (
                User.objects.select_for_update()
                .select_related("primary_role")
                .filter(pk=actor.pk)
                .first()
            )
            permissions = (
                set(auth_service.effective_permission_codes(actor)) if actor is not None else set()
            )
            roles = (
                set(auth_service.effective_role_codes(actor)) if actor is not None else set()
            )
            if (
                actor is None
                or not actor.can_authenticate()
                or CREATE_PERMISSION not in permissions
                or "credit_manager" not in roles
            ):
                raise DomainPermissionDenied(
                    "You do not have SAP request create permission."
                )
            application, access = application_authority.resolve_application_access(
                application_id=application_id,
                actor=actor,
                required_permission=CREATE_PERMISSION,
                actor_permissions=permissions,
            )
            if application is None or not access.allowed:
                raise DomainObjectAccessDenied(access)
            application = (
                LoanApplication.objects.select_for_update()
                .select_related("member")
                .get(pk=application.pk)
            )
            member = application.member
            if SapCustomerCode.objects.select_for_update().filter(
                member=member, status=SapCustomerCode.STATUS_ACTIVE
            ).exists():
                raise SapRequestConflict(
                    "An active SAP customer code already exists for this member."
                )
            replay = (
                SapCustomerProfileRequest.objects.select_for_update()
                .select_related("assigned_to_user")
                .filter(
                    loan_application=application,
                    request_status__in=SapCustomerProfileRequest.ACTIVE_STATUSES,
                )
                .first()
            )
            if replay is not None:
                return serialize_request(replay)

            assignee = _active_assignee(values["assigned_to_user_id"])
            decision = _terminal_decision(application)
            facts = _canonical_facts(application, member, decision)
            bank = resolve_blank_cheque_bank_fact(application_id=application.pk)
            if bank.valid:
                facts["bank_account_last4"] = (bank.bank_account_masked or "")[-4:]
                facts["ifsc"] = bank.ifsc or ""

            request_id = uuid.uuid4()
            file_id = uuid.uuid4()
            workbook = render_annexure_i(_workbook_values(facts))
            upload = SimpleUploadedFile(
                f"annexure-i-{application.application_reference_number}.xlsx",
                workbook,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            stored_file = storage.store(upload)
            document = DocumentFile.objects.create(
                document_id=file_id,
                file_name=upload.name,
                file_extension=".xlsx",
                mime_type=upload.content_type,
                file_size_bytes=stored_file.file_size_bytes,
                storage_provider=stored_file.storage_provider,
                storage_key=stored_file.storage_key,
                checksum_sha256=stored_file.checksum_sha256,
                uploaded_by_user=actor,
                sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
            )
            row = SapCustomerProfileRequest.objects.create(
                sap_customer_profile_request_id=request_id,
                loan_application=application,
                member=member,
                requested_by_user=actor,
                assigned_to_user=assignee,
                excel_file=document,
                **facts,
            )
            safe_evidence = {
                "sap_customer_profile_request_id": str(row.pk),
                "loan_application_id": str(application.pk),
                "member_id": str(member.pk),
                "excel_file_id": str(document.pk),
                "requested_by_user_id": str(actor.pk),
                "assigned_to_user_id": str(assignee.pk),
                "request_status": row.request_status,
                "request_provenance": "manual_file_annexure_i",
                "outcome": "created",
                "request_id": request.headers.get("X-Request-ID"),
            }
            AuditLog.objects.create(
                actor_user=actor,
                actor_type="user",
                action="finance.sap_customer_code.requested",
                entity_type="sap_customer_profile_request",
                entity_id=row.pk,
                old_value_json=None,
                new_value_json=safe_evidence,
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            )
            record_workflow_event(
                actor=actor,
                workflow_name="SAPCustomerCodeRequested",
                entity_type="sap_customer_profile_request",
                entity_id=row.pk,
                from_state=None,
                to_state=SapCustomerProfileRequest.STATUS_DRAFT,
                trigger_reason="finance.sap_customer_code.requested",
                action_code="finance.sap_customer_code.requested",
                metadata=safe_evidence,
            )
            return serialize_request(row)
    except Exception:
        if stored_file is not None:
            storage.delete(stored_file)
        raise


def serialize_request(row):
    return {
        "sap_customer_profile_request_id": str(row.pk),
        "request_status": row.request_status,
        "excel_file_id": str(row.excel_file_id),
        "assigned_to_user": {
            "user_id": str(row.assigned_to_user_id),
            "full_name": row.assigned_to_user.full_name,
        },
    }


def _parse_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"body": "A JSON object is required."})
    allowed = {"assigned_to_user_id"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    if "assigned_to_user_id" not in payload:
        errors["assigned_to_user_id"] = "This field is required."
    if errors:
        raise ValidationError(errors)
    try:
        assignee_id = uuid.UUID(str(payload["assigned_to_user_id"]))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValidationError(
            {"assigned_to_user_id": "Must be a valid UUID."}
        ) from exc
    return {"assigned_to_user_id": assignee_id}


def _active_assignee(user_id):
    assignee = User.objects.select_for_update().select_related("primary_role").filter(
        pk=user_id,
        status=User.ACTIVE_STATUS,
        primary_role__role_code="senior_manager_finance",
        primary_role__status="active",
    ).first()
    if assignee is None:
        raise ValidationError(
            {"assigned_to_user_id": "Select an active Senior Manager Finance user."}
        )
    return assignee


def _terminal_decision(application):
    latest_case = (
        ApprovalCase.objects.select_for_update()
        .filter(loan_application=application)
        .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
        .first()
    )
    decision = (
        SanctionDecision.objects.select_for_update()
        .filter(loan_application=application, approval_case=latest_case, decision="sanctioned")
        .first()
        if latest_case else None
    )
    if (
        application.application_status != LoanApplication.STATUS_APPROVED_BY_SANCTION
        or latest_case is None
        or latest_case.current_status != ApprovalCase.STATUS_APPROVED
        or decision is None
        or decision.sanctioned_amount is None
        or decision.sanctioned_amount <= Decimal("0.00")
        or decision.recorded_at is None
    ):
        raise DomainInvalidStateError(
            "A current terminal sanctioned decision is required."
        )
    return decision


def _canonical_facts(application, member, decision):
    required = {
        "farmer_full_name": member.legal_name,
        "borrower_type": member.member_type,
        "folio_number": member.folio_number,
        "loan_application_number": application.application_reference_number,
        "registered_address_line1": member.registered_address_line1,
        "registered_village_city": member.registered_village_city,
        "registered_district": member.registered_district,
        "registered_state": member.registered_state,
        "registered_pincode": member.registered_pincode,
    }
    missing = [field for field, value in required.items() if not str(value or "").strip()]
    if missing:
        raise ValidationError({field: "Canonical source value is required." for field in missing})
    pan = _identity_value("pan", member.pan_encrypted, _PAN)
    aadhaar = ""
    if member.member_type == "individual_farmer":
        aadhaar = _identity_value("aadhaar", member.aadhaar_encrypted, _AADHAAR)
    address = ", ".join(
        part.strip() for part in (
            member.registered_address_line1, member.registered_address_line2,
            member.registered_village_city, member.registered_district,
            member.registered_state, member.registered_pincode,
        ) if part and part.strip()
    )
    return {
        "farmer_full_name": member.legal_name.strip(),
        "borrower_type": member.member_type,
        "folio_number": member.folio_number.strip(),
        "aadhaar_number_encrypted": (
            FieldEncryption.encrypt("finance.sap_request.aadhaar", aadhaar) if aadhaar else ""
        ),
        "pan_number_encrypted": FieldEncryption.encrypt("finance.sap_request.pan", pan),
        "address_text": address,
        "email_id": member.email or "",
        "mobile_number": member.mobile_number or "",
        "loan_application_number": application.application_reference_number,
        "sanctioned_amount": decision.sanctioned_amount,
        "sanction_date": decision.recorded_at.date(),
        "bank_account_last4": "",
        "ifsc": "",
        "_plain_pan": pan,
        "_plain_aadhaar": aadhaar,
    }


def _identity_value(label, stored_value, pattern):
    value = str(stored_value or "").strip()
    if not value.startswith("field:v2:"):
        raise ValidationError({label: "Canonical source value is unavailable."})
    try:
        value = FieldEncryption.decrypt(f"members.{label}", value)
    except InvalidCiphertext as exc:
        raise ValidationError({label: "Canonical source value is unavailable."}) from exc
    if not pattern.fullmatch(value):
        raise ValidationError({label: "Canonical source value is unavailable."})
    return value


def _workbook_values(facts):
    values = (
        facts["loan_application_number"], facts["farmer_full_name"],
        facts["borrower_type"], facts.pop("_plain_aadhaar"), facts.pop("_plain_pan"),
        facts["address_text"], facts["email_id"], facts["mobile_number"],
        facts["folio_number"], f'{facts["sanctioned_amount"]:.2f}',
        facts["sanction_date"].isoformat(), facts["bank_account_last4"], facts["ifsc"],
    )
    return values
