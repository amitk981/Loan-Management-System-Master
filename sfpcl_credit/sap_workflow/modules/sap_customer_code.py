import hashlib
import json
import uuid
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.communications.services import create_internal_user_task
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.services import resolve_immutable_upload_provenance
from sfpcl_credit.domain_errors import DomainInvalidStateError, DomainObjectAccessDenied, DomainPermissionDenied
from sfpcl_credit.sap_workflow.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.sap_workflow.modules.annexure_storage import EncryptedAnnexureStorage
from sfpcl_credit.sap_workflow.modules.sap_customer_request import SapRequestConflict, current_terminal_sanction
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import Member
from sfpcl_credit.sap_workflow.adapters import ManualSapAdapter, SapCustomerProfilePayload
from sfpcl_credit.workflows.events import record_workflow_event
SEND_PERMISSION = "finance.sap_request.send"
COMPLETE_PERMISSION = "finance.sap_request.complete"
READ_PERMISSION = "finance.sap_code.read"
_INACCESSIBLE_DOCUMENT = "Document file was not found or is inaccessible."
def send_request(*, actor, request_id, payload, request, storage=None, adapter=None):
    values = _parse_send_payload(payload)
    adapter = adapter or ManualSapAdapter()
    with transaction.atomic():
        actor = _locked_actor(actor, SEND_PERMISSION, "credit_manager")
        row, application, member, assignee = _locked_request_scope(request_id, actor_id=actor.pk, owner_field="requested_by_user_id")
        _require_current_scope(row, application, member, assignee)
        if row.request_status == SapCustomerProfileRequest.STATUS_SENT:
            workbook = EncryptedAnnexureStorage(storage).read_verified(row.excel_file)
            checksum = hashlib.sha256(workbook).hexdigest()
            if row.sent_remarks != values["remarks"] or row.delivery_checksum_sha256 != checksum or row.delivery_storage_checksum_sha256 != row.excel_file.checksum_sha256 or row.delivery_file_id_snapshot != row.excel_file_id or row.delivery_assignee_id_snapshot != row.assigned_to_user_id or adapter.get_customer_status(row.delivery_reference).delivery_status != "delivered":
                raise SapRequestConflict("The sent SAP request facts cannot be changed.")
            return serialize_sent_request(row)
        if row.request_status != SapCustomerProfileRequest.STATUS_DRAFT:
            raise DomainInvalidStateError("Only a draft SAP request can be sent.")
        workbook = EncryptedAnnexureStorage(storage).read_verified(row.excel_file)
        if not workbook.startswith(b"PK"):
            raise DomainInvalidStateError("The retained SAP Annexure-I file is invalid.")
        checksum = hashlib.sha256(workbook).hexdigest()
        delivery = adapter.create_customer_profile_request(
            SapCustomerProfilePayload(request_id=row.pk, assignee_user_id=assignee.pk, document_id=row.excel_file_id, file_name=row.excel_file.file_name, mime_type=row.excel_file.mime_type or "", workbook_bytes=workbook, checksum_sha256=checksum), idempotency_key=f"sap-customer-profile:{row.pk}"
        )
        if delivery.delivery_status != "delivered" or delivery.checksum_sha256 != checksum:
            raise SapRequestConflict("The manual SAP adapter did not accept Annexure-I delivery.")
        communication, task = create_internal_user_task(
            sender=actor,
            recipient=assignee,
            related_entity_type="sap_customer_profile_request",
            related_entity_id=row.pk,
            subject="SAP customer profile creation request",
            body="A checksum-verified Annexure-I is ready in the governed SAP workspace.",
            action_label="Open SAP delivery",
            action_url=(f"/api/v1/sap-customer-profile-requests/{row.pk}/" "annexure-i-delivery-capability/"),
            notification_type="sap_customer_profile_request",
            category="Finance",
        )
        sent_at = timezone.now()
        row.request_status = SapCustomerProfileRequest.STATUS_SENT
        row.sent_at = sent_at
        row.sent_remarks = values["remarks"]
        row.sent_communication = communication
        row.sent_task = task
        row.delivery_reference = delivery.external_reference
        row.delivery_checksum_sha256 = delivery.checksum_sha256
        row.delivery_storage_checksum_sha256 = row.excel_file.checksum_sha256
        row.delivery_file_id_snapshot = row.excel_file_id
        row.delivery_assignee_id_snapshot = row.assigned_to_user_id
        row.save(update_fields=["request_status", "sent_at", "sent_remarks", "sent_communication", "sent_task", "delivery_reference", "delivery_checksum_sha256", "delivery_storage_checksum_sha256", "delivery_file_id_snapshot", "delivery_assignee_id_snapshot"])
        communication.delivery_status = delivery.delivery_status
        communication.external_message_id = delivery.external_reference
        communication.save(update_fields=["delivery_status", "external_message_id"])
        evidence = _safe_evidence(row, actor, outcome="sent")
        evidence.update(
            {"communication_id": str(communication.pk), "task_id": str(task.pk), "excel_file_id": str(row.excel_file_id), "annexure_checksum_sha256": delivery.checksum_sha256, "delivery_reference": delivery.external_reference, "provenance": "manual_file_annexure_i", "request_id": request.headers.get("X-Request-ID")}
        )
        _record_audit(actor=actor, request=request, row=row, action="finance.sap_customer_code.sent", evidence=evidence)
        record_workflow_event(
            actor=actor,
            workflow_name="SAPCustomerCodeSent",
            entity_type="sap_customer_profile_request",
            entity_id=row.pk,
            from_state=SapCustomerProfileRequest.STATUS_DRAFT,
            to_state=SapCustomerProfileRequest.STATUS_SENT,
            trigger_reason="finance.sap_customer_code.sent",
            action_code="finance.sap_customer_code.sent",
            metadata=evidence,
        )
        return serialize_sent_request(row)
def complete_request(*, actor, request_id, payload, request):
    values = _parse_complete_payload(payload)
    completion_digest = _completion_input_digest(values)
    with transaction.atomic():
        actor = _locked_actor(actor, COMPLETE_PERMISSION, "senior_manager_finance")
        row, application, member, assignee = _locked_request_scope(request_id, actor_id=actor.pk, owner_field="assigned_to_user_id")
        _require_current_scope(row, application, member, assignee)
        if row.request_status == SapCustomerProfileRequest.STATUS_COMPLETED:
            _require_exact_completion_replay(row, values, completion_digest)
            return serialize_completed_request(row)
        if row.request_status != SapCustomerProfileRequest.STATUS_SENT:
            raise DomainInvalidStateError("Only a sent SAP request can be completed.")
        confirmation_document = _confirmation_document(actor=actor, row=row, document_id=values["confirmation_document_id"])
        active_code = SapCustomerCode.objects.select_for_update().filter(member=member, status=SapCustomerCode.STATUS_ACTIVE).first()
        inactive_member_code_exists = SapCustomerCode.objects.select_for_update().filter(member=member, status=SapCustomerCode.STATUS_INACTIVE).exists()
        code_owner = SapCustomerCode.objects.select_for_update().filter(sap_customer_code__iexact=values["sap_customer_code"]).first()
        if code_owner is not None and code_owner.member_id != member.pk:
            raise SapRequestConflict("The SAP customer code belongs to another member.")
        if active_code is None and inactive_member_code_exists:
            raise SapRequestConflict("This member has inactive SAP code history requiring governed correction.")
        reused = active_code is not None
        if active_code is not None:
            if active_code.sap_customer_code.upper() != values["sap_customer_code"]:
                raise SapRequestConflict("This member already has a different active SAP code.")
            _require_reuse_facts(active_code, values, confirmation_document)
            origin = SapCustomerProfileRequest.objects.select_for_update().filter(sap_customer_code=active_code, request_status=SapCustomerProfileRequest.STATUS_COMPLETED).exclude(pk=row.pk).order_by("completed_at", "sap_customer_profile_request_id").first()
            if origin is not None and origin.completed_at > row.created_at:
                raise SapRequestConflict("Another request for this member completed with the active SAP code.")
            code = active_code
        else:
            try:
                with transaction.atomic():
                    code = SapCustomerCode.objects.create(
                        member=member,
                        sap_customer_code=values["sap_customer_code"],
                        sap_vendor_code=values["sap_vendor_code"],
                        created_for_loan_application=application,
                        created_by_user=actor,
                        created_at_sap=values["created_at_sap"],
                        confirmation_document=confirmation_document,
                        confirmation_notes=values["confirmation_notes"],
                        status=SapCustomerCode.STATUS_ACTIVE,
                    )
            except IntegrityError as exc:
                raise SapRequestConflict("The SAP customer code or active member code already exists.") from exc
        row.request_status = SapCustomerProfileRequest.STATUS_COMPLETED
        row.completed_at = timezone.now()
        row.sap_customer_code = code
        row.completion_reused_existing_code = reused
        row.completion_input_digest = completion_digest
        row.save(update_fields=["request_status", "completed_at", "sap_customer_code", "completion_reused_existing_code", "completion_input_digest"])
        evidence = _safe_evidence(row, actor, outcome="reused" if reused else "created")
        evidence.update({"sap_customer_code_id": str(code.pk), "confirmation_document_id": (str(code.confirmation_document_id) if code.confirmation_document_id else None), "reuse": reused, "completion_input_digest": completion_digest, "provenance": "manual_sap_confirmation", "request_id": request.headers.get("X-Request-ID")})
        completion_action = "sap.customer_code_reused" if reused else "sap.customer_code_created"
        _record_audit(actor=actor, request=request, row=row, action=completion_action, evidence=evidence)
        record_workflow_event(
            actor=actor, workflow_name="SAPCustomerCodeCompleted", entity_type="sap_customer_profile_request", entity_id=row.pk, from_state=SapCustomerProfileRequest.STATUS_SENT, to_state=SapCustomerProfileRequest.STATUS_COMPLETED, trigger_reason=completion_action, action_code=completion_action, metadata=evidence
        )
        return serialize_completed_request(row)
def read_member_code(*, actor, member_id, request):
    with transaction.atomic():
        actor = _locked_actor(actor, READ_PERMISSION, "senior_manager_finance")
        member = Member.objects.select_for_update().filter(pk=member_id, is_deleted=False, membership_status="active").first()
        if member is None:
            raise DomainObjectAccessDenied(None)
        scoped_request = SapCustomerProfileRequest.objects.select_for_update().filter(member=member, assigned_to_user=actor, request_status=SapCustomerProfileRequest.STATUS_COMPLETED, sap_customer_code__isnull=False).order_by("-completed_at", "-sap_customer_profile_request_id").first()
        if scoped_request is None:
            raise DomainObjectAccessDenied(None)
        code = SapCustomerCode.objects.select_for_update().filter(member=member, status=SapCustomerCode.STATUS_ACTIVE).first()
        if code is None or scoped_request.sap_customer_code_id != code.pk:
            raise DomainInvalidStateError("An active SAP customer code is unavailable.")
        _record_audit(actor=actor, request=request, row=scoped_request, action="sap.customer_code_read", evidence=_safe_evidence(scoped_request, actor, outcome="read"))
        return serialize_member_code(code)
def serialize_sent_request(row):
    return {
        "sap_customer_profile_request_id": str(row.pk),
        "request_status": row.request_status,
        "sent_at": _iso(row.sent_at),
        "assigned_to_user": {"user_id": str(row.assigned_to_user_id), "full_name": row.assigned_to_user.full_name},
        "communication_id": str(row.sent_communication_id),
        "task_id": str(row.sent_task_id),
        "delivery": {"delivery_reference": row.delivery_reference, "checksum_sha256": row.delivery_checksum_sha256, "document_id": str(row.delivery_file_id_snapshot), "capability_path": (f"/api/v1/sap-customer-profile-requests/{row.pk}/" "annexure-i-delivery-capability/")},
    }
def serialize_completed_request(row):
    code = row.sap_customer_code
    return {
        "sap_customer_profile_request_id": str(row.pk),
        "sap_customer_code_id": str(code.pk),
        "member_id": str(row.member_id),
        "loan_application_id": str(row.loan_application_id),
        "request_status": row.request_status,
        "completed_at": _iso(row.completed_at),
        "reuse": bool(row.completion_reused_existing_code),
        "sap_customer_code_masked": _masked(code.sap_customer_code),
        "sap_vendor_code_masked": _masked(code.sap_vendor_code),
        "confirmation_document": ({"document_id": str(code.confirmation_document_id), "file_name": code.confirmation_document.file_name, "mime_type": code.confirmation_document.mime_type, "sensitivity_level": code.confirmation_document.sensitivity_level} if code.confirmation_document_id else None),
    }
def serialize_member_code(code):
    return {"sap_customer_code_id": str(code.pk), "member_id": str(code.member_id), "sap_customer_code_masked": _masked(code.sap_customer_code), "sap_vendor_code_masked": _masked(code.sap_vendor_code), "status": code.status}
def _locked_actor(actor, permission, role):
    persisted = User.objects.select_for_update().select_related("primary_role").filter(pk=getattr(actor, "pk", None)).first()
    permissions = set(auth_service.effective_permission_codes(persisted)) if persisted else set()
    roles = set(auth_service.effective_role_codes(persisted)) if persisted else set()
    if persisted is None or not persisted.can_authenticate() or permission not in permissions or role not in roles:
        raise DomainPermissionDenied(f"You do not have {permission} permission.")
    return persisted
def _locked_request_scope(request_id, *, actor_id, owner_field):
    reference = SapCustomerProfileRequest.objects.filter(pk=request_id).values("loan_application_id", "member_id", "requested_by_user_id", "assigned_to_user_id").first()
    if reference is None or reference[owner_field] != actor_id:
        raise DomainObjectAccessDenied(None)
    application = LoanApplication.objects.select_for_update().select_related("member").filter(pk=reference["loan_application_id"]).first()
    member = Member.objects.select_for_update().filter(pk=reference["member_id"]).first()
    if application is None or member is None:
        raise DomainObjectAccessDenied(None)
    current_terminal_sanction(application)
    row = SapCustomerProfileRequest.objects.select_for_update(of=("self",)).select_related("assigned_to_user__primary_role", "excel_file", "sent_communication", "sent_task", "sap_customer_code__confirmation_document").get(pk=request_id)
    assignee = User.objects.select_for_update().select_related("primary_role").filter(pk=row.assigned_to_user_id).first()
    if assignee is None:
        raise DomainObjectAccessDenied(None)
    return row, application, member, assignee
def _require_current_scope(row, application, member, assignee):
    decision = current_terminal_sanction(application)
    if (
        application.member_id != member.pk
        or row.member_id != member.pk
        or row.loan_application_id != application.pk
        or row.sanction_decision_id_snapshot != decision.pk
        or row.sanction_approval_case_id_snapshot != decision.approval_case_id
        or row.sanctioned_amount != decision.sanctioned_amount
        or row.sanction_date != decision.recorded_at.date()
        or member.is_deleted
        or member.membership_status != "active"
        or not assignee.can_authenticate()
        or assignee.primary_role.status != "active"
        or assignee.primary_role.role_code != "senior_manager_finance"
    ):
        raise DomainInvalidStateError("The SAP request is no longer bound to current terminal sanction evidence.")
def _confirmation_document(*, actor, row, document_id):
    if document_id is None:
        return None
    try:
        provenance = resolve_immutable_upload_provenance(document_id=document_id)
    except ValidationError as exc:
        raise ValidationError({"confirmation_document_id": _INACCESSIBLE_DOCUMENT}) from exc
    allowed_scope = (provenance.related_entity_type == "sap_customer_profile_request" and provenance.related_entity_id == row.pk) or (provenance.related_entity_type == "loan_application" and provenance.related_entity_id == row.loan_application_id)
    if provenance.document_category != "sap_confirmation" or not allowed_scope or provenance.document.uploaded_by_user_id != actor.pk or provenance.document.sensitivity_level != DocumentFile.SENSITIVITY_RESTRICTED:
        raise ValidationError({"confirmation_document_id": _INACCESSIBLE_DOCUMENT})
    return provenance.document
def _require_reuse_facts(code, values, document):
    comparisons = ((values["sap_vendor_code"], code.sap_vendor_code), (values["created_at_sap"], code.created_at_sap), (document.pk if document else None, code.confirmation_document_id), (values["confirmation_notes"], code.confirmation_notes))
    for supplied, retained in comparisons:
        if supplied not in (None, "") and supplied != retained:
            raise SapRequestConflict("Existing SAP customer code facts cannot be changed.")
def _require_exact_completion_replay(row, values, completion_digest):
    if not row.completion_input_digest or row.completion_input_digest != completion_digest:
        raise SapRequestConflict("The completed SAP request facts cannot be changed.")
    code = row.sap_customer_code
    if code is None or code.sap_customer_code != values["sap_customer_code"]:
        raise SapRequestConflict("The completed SAP request facts cannot be changed.")
    if row.completion_reused_existing_code:
        return
    if code.sap_vendor_code != values["sap_vendor_code"] or code.created_at_sap != values["created_at_sap"] or code.confirmation_document_id != values["confirmation_document_id"] or code.confirmation_notes != values["confirmation_notes"]:
        raise SapRequestConflict("The completed SAP request facts cannot be changed.")
def _parse_send_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"body": "A JSON object is required."})
    unknown = set(payload) - {"remarks"}
    if unknown:
        raise ValidationError({field: "Unknown field." for field in sorted(unknown)})
    remarks = payload.get("remarks", "")
    if not isinstance(remarks, str):
        raise ValidationError({"remarks": "Must be a string."})
    return {"remarks": remarks.strip()}
def _parse_complete_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"body": "A JSON object is required."})
    allowed = {"sap_customer_code", "sap_vendor_code", "created_at_sap", "confirmation_document_id", "confirmation_notes"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    customer_code = _code_value(payload.get("sap_customer_code"), "sap_customer_code", required=True, errors=errors)
    vendor_code = _code_value(payload.get("sap_vendor_code"), "sap_vendor_code", required=False, errors=errors)
    created_at_sap = None
    raw_created_at = payload.get("created_at_sap")
    if raw_created_at not in (None, ""):
        created_at_sap = parse_datetime(raw_created_at) if isinstance(raw_created_at, str) else None
        if created_at_sap is None or not timezone.is_aware(created_at_sap):
            errors["created_at_sap"] = "Must be an ISO-8601 timezone-aware timestamp."
        elif created_at_sap > timezone.now():
            errors["created_at_sap"] = "Must not be in the future."
    document_id = None
    raw_document_id = payload.get("confirmation_document_id")
    if raw_document_id not in (None, ""):
        try:
            document_id = uuid.UUID(str(raw_document_id))
        except (ValueError, TypeError, AttributeError):
            errors["confirmation_document_id"] = "Must be a valid UUID."
    notes = payload.get("confirmation_notes", "")
    if notes is None:
        notes = ""
    if not isinstance(notes, str):
        errors["confirmation_notes"] = "Must be a string."
        notes = ""
    if errors:
        raise ValidationError(errors)
    return {"sap_customer_code": customer_code, "sap_vendor_code": vendor_code, "created_at_sap": created_at_sap, "confirmation_document_id": document_id, "confirmation_notes": notes.strip(), "provided_fields": frozenset(payload)}
def _completion_input_digest(values):
    canonical = {}
    for field in ("sap_customer_code", "sap_vendor_code", "created_at_sap", "confirmation_document_id", "confirmation_notes"):
        value = values[field]
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        elif value is not None:
            value = str(value)
        canonical[field] = {"provided": field in values["provided_fields"], "value": value}
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
def _code_value(raw, field, *, required, errors):
    if raw is None:
        raw = ""
    if not isinstance(raw, str):
        errors[field] = "Must be a string."
        return ""
    value = raw.strip().upper()
    if required and not value:
        errors[field] = "This field is required."
    elif len(value) > 120:
        errors[field] = "Must be 120 characters or fewer."
    return value
def _record_audit(*, actor, request, row, action, evidence):
    read_only = action == "sap.customer_code_read"
    evidence = {
        **evidence,
        "actor_type": "user",
        "actor_role_codes": sorted(auth_service.effective_role_codes(actor)),
        "actor_team_codes": sorted(actor.team_codes()),
        "action": action,
        "entity_type": "sap_customer_profile_request",
        "entity_id": str(row.pk),
        "old_state": (row.request_status if read_only else SapCustomerProfileRequest.STATUS_DRAFT if row.request_status == SapCustomerProfileRequest.STATUS_SENT else SapCustomerProfileRequest.STATUS_SENT),
        "new_state": row.request_status,
        "request_id": request.headers.get("X-Request-ID"),
        "ip_address": request_ip(request),
        "user_agent": request_user_agent(request),
        "timestamp": _iso(timezone.now()),
        "reason": ("Authorised masked SAP customer code read." if read_only else "SAP customer profile workflow action accepted."),
    }
    evidence_digest = hashlib.sha256(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    selector_manifest_json = json.dumps(
        evidence, sort_keys=True, separators=(",", ":")
    )
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="sap_customer_profile_request",
        entity_id=row.pk,
        old_value_json={
            "request_status": evidence["old_state"],
            "evidence_sha256": evidence_digest,
            "request_id": evidence["request_id"],
            "timestamp": evidence["timestamp"],
            "selector_manifest": evidence,
        },
        new_value_json=evidence,
        selector_manifest_json=selector_manifest_json,
        selector_manifest_sha256=evidence_digest,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
def _safe_evidence(row, actor, *, outcome):
    return {
        "sap_customer_profile_request_id": str(row.pk),
        "loan_application_id": str(row.loan_application_id),
        "member_id": str(row.member_id),
        "sanction_decision_id": str(row.sanction_decision_id_snapshot),
        "sanction_approval_case_id": str(row.sanction_approval_case_id_snapshot),
        "actor_user_id": str(actor.pk),
        "assigned_to_user_id": str(row.assigned_to_user_id),
        "request_status": row.request_status,
        "outcome": outcome,
    }
def _masked(value):
    value = value or ""
    if not value:
        return ""
    visible = min(4, len(value))
    return "*" * (len(value) - visible) + value[-visible:]
def _iso(value):
    return value.isoformat().replace("+00:00", "Z") if value else None
