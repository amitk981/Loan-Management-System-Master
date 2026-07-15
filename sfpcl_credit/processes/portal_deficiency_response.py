"""Borrower-owned application deficiency response workflow."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import (
    ApplicationDeficiency,
    ApplicationDeficiencyResponse,
    ApplicationDeficiencyResponseDraft,
    LoanApplication,
)
from sfpcl_credit.applications import services as application_services
from sfpcl_credit.applications.modules import loan_application_lifecycle
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog, PortalAccount
from sfpcl_credit.processes import portal_application_scope
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.models import WorkflowEvent


class PortalDeficiencyNotFound(Exception):
    pass


@dataclass(frozen=True)
class PortalDeficiencyContent:
    body: bytes
    file_name: str
    mime_type: str


def resolve_context(*, actor, application_id):
    try:
        return portal_application_scope.resolve(
            actor=actor, application_id=application_id
        )
    except portal_application_scope.PortalApplicationScopeNotFound as exc:
        raise PortalDeficiencyNotFound from exc


def audit_access_denied(*, actor, application_id, attempted_action, request):
    account = PortalAccount.objects.filter(
        user=actor, status=PortalAccount.STATUS_ACTIVE
    ).first()
    if account is None:
        return
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account",
        action="portal.deficiency.access_denied",
        entity_type="loan_application",
        entity_id=application_id,
        old_value_json=None,
        new_value_json={
            "portal_account_id": str(account.pk),
            "member_id": str(account.member_id),
            "attempted_action": attempted_action,
            "request_id": request.headers.get("X-Request-ID"),
            "outcome": "denied",
        },
        ip_address=_request_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
    )


def get_projection(*, actor, application_id, request):
    context = resolve_context(actor=actor, application_id=application_id)
    items = list(
        ApplicationDeficiency.objects.filter(
            loan_application=context.application,
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
        ).order_by("item_code", "raised_at", "deficiency_id")
    )
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account",
        action="portal.deficiency.viewed",
        entity_type="loan_application",
        entity_id=context.application.pk,
        old_value_json=None,
        new_value_json={
            "portal_account_id": str(context.account.pk),
            "member_id": str(context.account.member_id),
            "loan_application_id": str(context.application.pk),
            "open_deficiency_count": len(items),
            "request_id": request.headers.get("X-Request-ID"),
            "outcome": "accepted",
        },
        ip_address=_request_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
    )
    responses = {
        row.deficiency_id: row
        for row in ApplicationDeficiencyResponse.objects.filter(
            deficiency__loan_application=context.application,
            successor__isnull=True,
        ).select_related("document", "portal_account")
    }
    response_states = _resolve_response_states(responses.values())
    drafts = {
        row.deficiency_id: row
        for row in ApplicationDeficiencyResponseDraft.objects.filter(
            deficiency__loan_application=context.application,
            portal_account=context.account,
        )
    }
    return {
        "loan_application_id": str(context.application.pk),
        "application_reference_number": context.application.application_reference_number,
        "application_status": context.application.application_status,
        "deficiency_note_action_url": (
            f"/api/v1/portal/applications/{context.application.pk}/deficiencies/note/"
        ),
        "resubmission_allowed": (
            context.application.application_status
            == LoanApplication.STATUS_INCOMPLETE_RETURNED
            and bool(items)
            and all(
                item.pk in responses
                and response_states.get(responses[item.pk].pk) == "responded"
                for item in items
            )
        ),
        "items": [
            {
                "deficiency_id": str(item.pk),
                "item_code": item.item_code,
                "deficiency_type": item.deficiency_type,
                "description": item.description,
                "resolution_status": item.resolution_status,
                "raised_at": item.raised_at.isoformat().replace("+00:00", "Z"),
                "upload_contract": {
                    "document_category": _expected_document_category(item.item_code),
                    "sensitivity_level": "confidential",
                    "allowed_extensions": ["pdf", "jpg", "jpeg", "png"],
                    "max_size_bytes": 5 * 1024 * 1024,
                },
                "response": _serialize_response(
                    responses.get(item.pk), response_states=response_states
                ),
                "draft": _serialize_draft(drafts.get(item.pk)),
            }
            for item in items
        ],
    }


@transaction.atomic
def save_draft(*, actor, application_id, deficiency_id, payload, request):
    context = resolve_context(actor=actor, application_id=application_id)
    application = LoanApplication.objects.select_for_update().get(pk=context.application.pk)
    if application.application_status != LoanApplication.STATUS_INCOMPLETE_RETURNED:
        raise PortalDeficiencyUnavailable(
            "Deficiency response drafts require an application returned for rectification."
        )
    deficiency = ApplicationDeficiency.objects.filter(
        pk=deficiency_id,
        loan_application=application,
        resolution_status=ApplicationDeficiency.STATUS_OPEN,
    ).first()
    if deficiency is None:
        raise PortalDeficiencyNotFound
    unknown = sorted(set(payload) - {"response_remark"})
    remark = payload.get("response_remark", "")
    errors = {}
    if unknown:
        errors["unknown_fields"] = f"Unknown fields: {', '.join(unknown)}."
    if not isinstance(remark, str):
        errors["response_remark"] = "Must be a string."
    else:
        remark = remark.strip()
        if len(remark) > 4000:
            errors["response_remark"] = "Must not exceed 4000 characters."
    if errors:
        raise PortalDeficiencyValidationError(errors)
    draft, _created = ApplicationDeficiencyResponseDraft.objects.update_or_create(
        deficiency=deficiency,
        defaults={
            "portal_account": context.account,
            "member": context.account.member,
            "response_remark": remark,
            "updated_at": timezone.now(),
        },
    )
    _audit(
        actor=actor,
        action="portal.deficiency.draft_saved",
        entity=draft,
        payload={
            "portal_account_id": str(context.account.pk),
            "member_id": str(context.account.member_id),
            "loan_application_id": str(application.pk),
            "deficiency_id": str(deficiency.pk),
            "has_response_remark": bool(remark),
            "request_id": request.headers.get("X-Request-ID"),
            "outcome": "accepted",
        },
        request=request,
    )
    return {"deficiency_id": str(deficiency.pk), **_serialize_draft(draft)}


def deficiency_note(*, actor, application_id, request):
    context = resolve_context(actor=actor, application_id=application_id)
    items = list(
        ApplicationDeficiency.objects.filter(
            loan_application=context.application,
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
        ).order_by("item_code", "raised_at", "deficiency_id")
    )
    lines = [
        "SFPCL Application Deficiency Note",
        f"Application: {context.application.application_reference_number or context.application.pk}",
        "",
    ]
    lines.extend(f"- {item.description}" for item in items)
    _audit(
        actor=actor,
        action="portal.deficiency.note_downloaded",
        entity=context.application,
        payload={
            "portal_account_id": str(context.account.pk),
            "member_id": str(context.account.member_id),
            "loan_application_id": str(context.application.pk),
            "open_deficiency_count": len(items),
            "request_id": request.headers.get("X-Request-ID"),
            "outcome": "accepted",
        },
        request=request,
    )
    return PortalDeficiencyContent(
        body=("\n".join(lines) + "\n").encode("utf-8"),
        file_name="application-deficiency-note.txt",
        mime_type="text/plain; charset=utf-8",
    )


@transaction.atomic
def upload(*, actor, application_id, deficiency_id, request):
    context = resolve_context(actor=actor, application_id=application_id)
    application = LoanApplication.objects.select_for_update().get(pk=context.application.pk)
    if application.application_status != LoanApplication.STATUS_INCOMPLETE_RETURNED:
        raise PortalDeficiencyUnavailable(
            "Deficiency responses require an application returned for rectification."
        )
    deficiency = (
        ApplicationDeficiency.objects.select_for_update()
        .filter(
            pk=deficiency_id,
            loan_application=application,
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
        )
        .first()
    )
    if deficiency is None:
        raise PortalDeficiencyNotFound
    cleaned = _validate_upload_request(request, deficiency)
    previous = (
        ApplicationDeficiencyResponse.objects.select_for_update()
        .filter(deficiency=deficiency, successor__isnull=True)
        .order_by("-created_at", "-application_deficiency_response_id")
        .first()
    )
    document_version = (
        ApplicationDeficiencyResponse.objects.filter(deficiency=deficiency).count() + 1
    )
    document = document_services.store_document_upload(
        user=actor,
        request=request,
        uploaded_file=cleaned["file"],
        document_category=cleaned["document_category"],
        sensitivity_level=cleaned["sensitivity_level"],
        related_entity_type="application",
        related_entity_id=application.pk,
        audit_spec=document_services.DocumentAuditSpec(
            action="portal.document.uploaded",
            actor_type="portal_account",
            metadata={
                "portal_account_id": str(context.account.pk),
                "member_id": str(context.account.member_id),
                "loan_application_id": str(application.pk),
                "action_code": deficiency.item_code,
                "deficiency_id": str(deficiency.pk),
                "document_version": document_version,
                "document_category": cleaned["document_category"],
                "sensitivity_level": cleaned["sensitivity_level"],
                "reason": "borrower_portal_deficiency_response",
                "request_id": request.headers.get("X-Request-ID"),
                "network": {
                    "ip_address": document_services.request_ip(request),
                    "user_agent": document_services.request_user_agent(request),
                },
                "outcome": "accepted",
            },
        ),
    )
    party_type, party_id = _application_document_party(application, deficiency.item_code)
    application_document = application_services.attach_application_document(
        application,
        {
            "document_type": deficiency.item_code,
            "party_type": party_type,
            "party_id": str(party_id) if party_id else None,
            "document_file_id": str(document.pk),
            "remarks": cleaned["response_remark"],
        },
        actor,
        request_ip=_request_ip(request) or "",
        request_user_agent=request.headers.get("User-Agent", ""),
        request_id=request.headers.get("X-Request-ID"),
    )
    response = ApplicationDeficiencyResponse.objects.create(
        deficiency=deficiency,
        document=document,
        portal_account=context.account,
        uploader_member=context.account.member,
        response_remark=cleaned["response_remark"],
        supersedes=previous,
    )
    common = {
        "portal_account_id": str(context.account.pk),
        "member_id": str(context.account.member_id),
        "loan_application_id": str(application.pk),
        "deficiency_id": str(deficiency.pk),
        "deficiency_response_id": str(response.pk),
        "document_id": str(document.pk),
        "application_document_id": str(application_document.pk),
        "document_category": cleaned["document_category"],
        "sensitivity_level": cleaned["sensitivity_level"],
        "checksum_sha256": document.checksum_sha256,
        "prior_current_document_id": str(previous.document_id) if previous else None,
        "request_id": request.headers.get("X-Request-ID"),
        "outcome": "accepted",
    }
    _audit(actor=actor, action="portal.deficiency.responded", entity=response, payload=common, request=request)
    record_workflow_event(
        actor=actor,
        workflow_name="application_deficiency",
        entity_type="application_deficiency_response",
        entity_id=response.pk,
        from_state="responded" if previous else "absent",
        to_state="responded",
        trigger_reason="Borrower uploaded a deficiency response for completeness review.",
        action_code="respond",
    )
    return {
        "deficiency_id": str(deficiency.pk),
        "response_status": "responded",
        "response": _serialize_response(
            response, response_states=_resolve_response_states([response])
        ),
        "document": _serialize_document(document),
    }


@transaction.atomic
def resubmit(*, actor, application_id, request):
    context = resolve_context(actor=actor, application_id=application_id)
    application = LoanApplication.objects.select_for_update().get(pk=context.application.pk)
    if application.application_status != LoanApplication.STATUS_INCOMPLETE_RETURNED:
        raise PortalDeficiencyUnavailable(
            "Resubmission requires an application returned for rectification."
        )
    open_items = list(
        ApplicationDeficiency.objects.select_for_update()
        .filter(
            loan_application=application,
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
        )
        .order_by("item_code", "raised_at", "deficiency_id")
    )
    responses = list(
        ApplicationDeficiencyResponse.objects.select_for_update()
        .select_related("portal_account", "supersedes")
        .filter(deficiency__in=open_items, successor__isnull=True)
    )
    responses_by_deficiency = {response.deficiency_id: response for response in responses}
    response_states = _resolve_response_states(responses)
    missing = [
        item
        for item in open_items
        if item.pk not in responses_by_deficiency
        or response_states.get(responses_by_deficiency[item.pk].pk) != "responded"
    ]
    if not open_items or missing:
        raise PortalDeficiencyValidationError(
            {
                "deficiencies": (
                    "Every open deficiency must have a current replacement document before resubmission."
                )
            }
        )
    for deficiency in open_items:
        response = responses_by_deficiency[deficiency.pk]
        record_workflow_event(
            actor=actor,
            workflow_name="application_deficiency",
            entity_type="application_deficiency_response",
            entity_id=response.pk,
            from_state="responded",
            to_state="submitted_for_review",
            trigger_reason="Borrower resubmitted the response for staff completeness review.",
            action_code="resubmit",
        )
    payload = {
        "portal_account_id": str(context.account.pk),
        "member_id": str(context.account.member_id),
        "loan_application_id": str(application.pk),
        "responded_deficiency_ids": [str(item.pk) for item in open_items],
        "request_id": request.headers.get("X-Request-ID"),
        "outcome": "accepted",
    }
    application = loan_application_lifecycle.resubmit(
        application_id=application.pk,
        actor=actor,
        portal_scope=payload,
        request_metadata={
            "request_id": request.headers.get("X-Request-ID"),
            "ip_address": _request_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
        },
    )
    return {
        "loan_application_id": str(application.pk),
        "application_status": application.application_status,
        "completeness_status": application.completeness_status,
        "current_stage": application.current_stage,
        "pending_with": "SFPCL",
        "responded_deficiency_count": len(open_items),
    }


def download(*, actor, application_id, deficiency_id, request, storage=None):
    context = resolve_context(actor=actor, application_id=application_id)
    response = (
        ApplicationDeficiencyResponse.objects.select_related("document", "deficiency")
        .filter(
            deficiency_id=deficiency_id,
            deficiency__loan_application=context.application,
            successor__isnull=True,
        )
        .first()
    )
    if response is None:
        raise PortalDeficiencyNotFound
    scope = {
        "portal_account_id": str(context.account.pk),
        "member_id": str(context.account.member_id),
        "loan_application_id": str(context.application.pk),
        "deficiency_id": str(response.deficiency_id),
        "deficiency_response_id": str(response.pk),
    }
    if request.GET.get("content") != "1":
        capability = document_services.issue_download_capability(
            document=response.document,
            scope=scope,
        )
        query = urlencode({"content": "1", "token": capability["token"]})
        return {
            "download_url": (
                f"/api/v1/portal/applications/{context.application.pk}/deficiencies/"
                f"{response.deficiency_id}/download/?{query}"
            ),
            "expires_at": capability["expires_at"],
        }
    try:
        body = document_services.read_with_download_capability(
            document=response.document,
            scope=scope,
            token=request.GET.get("token", ""),
            storage=storage,
        )
    except ValidationError:
        raise PortalDeficiencyNotFound
    document_services.record_document_audit(
        user=actor,
        request=request,
        document=response.document,
        spec=document_services.DocumentAuditSpec(
            action="portal.document.downloaded",
            actor_type="portal_account",
            metadata={
                "portal_account_id": str(context.account.pk),
                "member_id": str(context.account.member_id),
                "loan_application_id": str(context.application.pk),
                "action_code": response.deficiency.item_code,
                "deficiency_id": str(response.deficiency_id),
                "deficiency_response_id": str(response.pk),
                "document_version": _response_version(response),
                "document_category": _expected_document_category(
                    response.deficiency.item_code
                ),
                "sensitivity_level": response.document.sensitivity_level,
                "reason": "borrower_portal_deficiency_response_download",
                "request_id": request.headers.get("X-Request-ID"),
                "network": {
                    "ip_address": document_services.request_ip(request),
                    "user_agent": document_services.request_user_agent(request),
                },
                "capability_verified": True,
                "outcome": "accepted",
            },
        ),
    )
    return PortalDeficiencyContent(
        body=body,
        file_name=response.document.file_name,
        mime_type=response.document.mime_type or "application/octet-stream",
    )


class PortalDeficiencyUnavailable(Exception):
    pass


class PortalDeficiencyValidationError(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Portal deficiency response failed validation.")


def _validate_upload_request(request, deficiency):
    allowed_fields = {
        "file",
        "document_category",
        "sensitivity_level",
        "response_remark",
    }
    unknown = sorted((set(request.POST.keys()) | set(request.FILES.keys())) - allowed_fields)
    errors = {}
    if unknown:
        errors["unknown_fields"] = f"Unknown fields: {', '.join(unknown)}."
    uploaded_file = request.FILES.get("file")
    if uploaded_file is None or len(request.FILES.getlist("file")) != 1:
        errors["file"] = "Exactly one file is required."
    elif uploaded_file.size <= 0:
        errors["file"] = "File must not be empty."
    elif uploaded_file.size > 5 * 1024 * 1024:
        errors["file"] = "File must not exceed 5 MiB."
    category = (request.POST.get("document_category") or "").strip().lower()
    if not category:
        errors["document_category"] = "This field is required."
    elif category not in {"kyc", "legal", "finance"}:
        errors["document_category"] = "Must be one of kyc, legal, finance."
    else:
        expected_category = _expected_document_category(deficiency.item_code)
        if category != expected_category:
            errors["document_category"] = (
                f"This deficiency requires the {expected_category} category."
            )
    sensitivity = (request.POST.get("sensitivity_level") or "").strip().lower()
    if not sensitivity:
        errors["sensitivity_level"] = "This field is required."
    elif sensitivity != "confidential":
        errors["sensitivity_level"] = "Must be confidential."
    remark = (request.POST.get("response_remark") or "").strip() or None
    if remark and len(remark) > 4000:
        errors["response_remark"] = "Must not exceed 4000 characters."
    if uploaded_file is not None:
        extension = Path(uploaded_file.name).suffix.lower()
        allowed_types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        if extension not in allowed_types or uploaded_file.content_type != allowed_types.get(extension):
            errors["file"] = "File extension and MIME type must be PDF, JPG, or PNG."
    if errors:
        raise ValidationError(errors)
    return {
        "file": uploaded_file,
        "document_category": category,
        "sensitivity_level": sensitivity,
        "response_remark": remark,
    }


def _expected_document_category(item_code):
    if item_code in {
        "borrower_pan",
        "borrower_aadhaar_ovd",
        "nominee_pan",
        "nominee_aadhaar_ovd",
    }:
        return "kyc"
    if item_code in {"six_month_bank_statement", "cancelled_cheque"}:
        return "finance"
    return "legal"


def _response_version(response):
    version = 1
    current = response
    while current.supersedes_id is not None:
        version += 1
        current = ApplicationDeficiencyResponse.objects.only("supersedes_id").get(
            pk=current.supersedes_id
        )
    return version


def _application_document_party(application, item_code):
    if item_code in {"nominee_pan", "nominee_aadhaar_ovd"}:
        return "nominee", application.nominee_id
    return "borrower", application.member_id


def _serialize_response(response, response_states=None):
    if response is None:
        return None
    response_states = response_states or {}
    return {
        "deficiency_response_id": str(response.pk),
        "response_status": response_states.get(response.pk, "evidence_invalid"),
        "response_remark": response.response_remark,
        "document": _serialize_document(response.document, response),
        "responded_at": response.created_at.isoformat().replace("+00:00", "Z"),
    }


def _resolve_response_states(responses):
    responses = list(responses)
    if not responses:
        return {}
    events_by_response = {response.pk: [] for response in responses}
    for event in WorkflowEvent.objects.filter(
        entity_id__in=events_by_response
    ).order_by("created_at", "workflow_event_id"):
        events_by_response[event.entity_id].append(event)

    states = {}
    for response in responses:
        events = events_by_response[response.pk]
        expected_actor_id = response.portal_account.user_id
        expected_from = "responded" if response.supersedes_id else "absent"
        response_event_valid = (
            len(events) >= 1
            and events[0].workflow_name == "application_deficiency"
            and events[0].entity_type == "application_deficiency_response"
            and events[0].from_state == expected_from
            and events[0].to_state == "responded"
            and events[0].triggered_by_user_id == expected_actor_id
            and events[0].trigger_reason
            == "Borrower uploaded a deficiency response for completeness review."
        )
        if len(events) == 1 and response_event_valid:
            states[response.pk] = "responded"
            continue
        submitted_event_valid = (
            len(events) == 2
            and events[1].workflow_name == "application_deficiency"
            and events[1].entity_type == "application_deficiency_response"
            and events[1].from_state == "responded"
            and events[1].to_state == "submitted_for_review"
            and events[1].triggered_by_user_id == expected_actor_id
            and events[1].trigger_reason
            == "Borrower resubmitted the response for staff completeness review."
        )
        states[response.pk] = (
            "submitted_for_review"
            if response_event_valid and submitted_event_valid
            else "evidence_invalid"
        )
    return states


def _serialize_draft(draft):
    if draft is None:
        return None
    return {
        "response_remark": draft.response_remark,
        "updated_at": draft.updated_at.isoformat().replace("+00:00", "Z"),
    }


def _serialize_document(document, response=None):
    data = {
        "document_id": str(document.pk),
        "file_name": document.file_name,
        "mime_type": document.mime_type,
        "file_size_bytes": document.file_size_bytes,
        "checksum_sha256": document.checksum_sha256,
        "uploaded_at": document.uploaded_at.isoformat().replace("+00:00", "Z"),
    }
    if response is not None:
        data["action_url"] = (
            f"/api/v1/portal/applications/{response.deficiency.loan_application_id}/"
            f"deficiencies/{response.deficiency_id}/download/"
        )
    return data


def _audit(*, actor, action, entity, payload, request):
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account",
        action=action,
        entity_type=entity._meta.db_table,
        entity_id=entity.pk,
        old_value_json=None,
        new_value_json=payload,
        ip_address=_request_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
    )


def _request_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",", 1)[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
