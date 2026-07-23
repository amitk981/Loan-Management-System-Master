import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, PortalAccount
from sfpcl_credit.members import services as member_services
from sfpcl_credit.members.models import (
    KycCorrectionRequest,
    KycDocument,
    KycProfile,
    Member,
    MemberIdentityChangeRequest,
)
from sfpcl_credit.members.modules.member_authority import (
    MemberObjectAccessDenied,
    evaluate_member_authority,
)
from sfpcl_credit.members.modules.member_registry import MemberRegistry
from sfpcl_credit.members.protected_identity import (
    identity_hash,
    mask_protected_identity,
    protected_identity_token,
)
from sfpcl_credit.workflows.events import record_workflow_event


ALLOWED_FIELDS = {"pan", "aadhaar", "mobile_number", "email", "registered_address"}
ALLOWED_DOCUMENT_TYPES = {"pan", "aadhaar", "photo", "ckyc_consent"}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024


class PortalKycCorrectionAccessDenied(Exception):
    pass


class KycCorrectionConflict(Exception):
    pass


def enforce_member_claim(*, user, member, payload, request_metadata):
    claimed = payload.get("member_id")
    if not claimed or str(claimed) == str(member.pk):
        return
    try:
        entity_id = uuid.UUID(str(claimed))
    except (TypeError, ValueError, AttributeError):
        entity_id = member.pk
    AuditLog.objects.create(
        actor_user=user,
        actor_type="portal_account",
        action="portal.kyc_correction.access_denied",
        entity_type="member",
        entity_id=entity_id,
        new_value_json={
            "authenticated_member_id": str(member.pk),
            "outcome": "denied",
            "reason": "cross_member_claim",
        },
        ip_address=request_metadata.get("ip_address", ""),
        user_agent=request_metadata.get("user_agent", ""),
    )
    raise PortalKycCorrectionAccessDenied("You cannot submit a correction for this member.")


def portal_account_for(*, user, member):
    return PortalAccount.objects.get(
        user=user,
        member=member,
        status=PortalAccount.STATUS_ACTIVE,
    )


def upload_evidence(*, user, member, request):
    document_type = str(request.POST.get("document_type") or "").strip()
    self_attested = str(request.POST.get("self_attested_flag") or "").lower() == "true"
    uploaded_file = request.FILES.get("file")
    errors = {}
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        errors["document_type"] = "Unsupported KYC document type."
    if document_type in {"pan", "aadhaar"} and not self_attested:
        errors["self_attested_flag"] = "Self-attestation is required for PAN and Aadhaar."
    if uploaded_file is None:
        errors["file"] = "A document file is required."
    elif getattr(uploaded_file, "size", 0) > MAX_FILE_SIZE:
        errors["file"] = "The document file must not exceed 10 MB."
    elif not any(uploaded_file.name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        errors["file"] = "Upload a PDF, JPG, JPEG, or PNG file."
    if errors:
        raise ValidationError(errors)
    account = portal_account_for(user=user, member=member)
    document = document_services.store_document_upload(
        user=user,
        request=request,
        uploaded_file=uploaded_file,
        document_category="kyc",
        sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        related_entity_type="member",
        related_entity_id=member.pk,
        provenance_metadata={
            "portal_account_id": str(account.pk),
            "member_id": str(member.pk),
            "document_type": document_type,
            "self_attested_flag": self_attested,
        },
        audit_spec=document_services.DocumentAuditSpec(
            action="portal.kyc_correction.evidence_uploaded",
            actor_type="portal_account",
            metadata={
                "portal_account_id": str(account.pk),
                "member_id": str(member.pk),
                "document_type": document_type,
                "self_attested_flag": self_attested,
            },
        ),
    )
    return document_services.serialize_document_file(document)


@transaction.atomic
def submit(*, user, member, payload, request_metadata):
    account = portal_account_for(user=user, member=member)
    member = type(member).objects.select_for_update().get(pk=member.pk)
    changes = payload.get("changes")
    reason = payload.get("reason")
    evidence_ids = payload.get("evidence_document_ids")
    errors = {}
    if not isinstance(changes, dict) or not changes:
        errors["changes"] = "At least one KYC field correction is required."
        changes = {}
    unknown = set(changes) - ALLOWED_FIELDS
    if unknown:
        errors["changes"] = "One or more KYC correction fields are unsupported."
    if not isinstance(reason, str) or not reason.strip():
        errors["reason"] = "A correction reason is required."
    if not isinstance(evidence_ids, list) or not evidence_ids:
        errors["evidence_document_ids"] = "At least one evidence document is required."
        evidence_ids = []
    pan = changes.get("pan")
    aadhaar = changes.get("aadhaar")
    if pan and (not isinstance(pan, str) or not member_services._PAN_RE.fullmatch(pan)):
        errors["pan"] = "Invalid PAN format."
    if aadhaar and (
        not isinstance(aadhaar, str) or not member_services._AADHAAR_RE.fullmatch(aadhaar)
    ):
        errors["aadhaar"] = "Invalid Aadhaar format."
    mobile_number = changes.get("mobile_number")
    if mobile_number is not None and (
        not isinstance(mobile_number, str) or not mobile_number.strip()
    ):
        errors["mobile_number"] = "A mobile number is required."
    email = changes.get("email")
    if email is not None:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."
    address = changes.get("registered_address")
    if address is not None and (
        not isinstance(address, dict)
        or not any(str(value).strip() for value in address.values())
    ):
        errors["registered_address"] = "Enter the corrected registered address."
    if member.kyc_status != "verified":
        errors["member"] = "Verified KYC is required for an identity correction."
    parsed_ids = []
    for raw in evidence_ids:
        try:
            parsed_ids.append(uuid.UUID(str(raw)))
        except (TypeError, ValueError, AttributeError):
            errors["evidence_document_ids"] = "Evidence document IDs must be valid UUIDs."
            break
    documents = list(DocumentFile.objects.filter(pk__in=parsed_ids))
    if len(documents) != len(set(parsed_ids)) or any(
        document.uploaded_by_user_id != user.pk
        or document.sensitivity_level != DocumentFile.SENSITIVITY_RESTRICTED
        or not AuditLog.objects.filter(
            action="portal.kyc_correction.evidence_uploaded",
            entity_id=document.pk,
            actor_user=user,
            new_value_json__member_id=str(member.pk),
        ).exists()
        for document in documents
    ):
        errors["evidence_document_ids"] = "Evidence was not found or is inaccessible."
    if errors:
        raise ValidationError(errors)

    identity_change = MemberIdentityChangeRequest.objects.create(
        member=member,
        requester_user=user,
        reason=reason.strip(),
        member_version=member.version,
        proposed_pan_encrypted=protected_identity_token(pan, 10) if pan else "",
        proposed_pan_hash=identity_hash(pan) if pan else "",
        proposed_aadhaar_encrypted=protected_identity_token(aadhaar, 12) if aadhaar else "",
        proposed_aadhaar_hash=identity_hash(aadhaar) if aadhaar else "",
    )
    correction = KycCorrectionRequest.objects.create(
        member=member,
        portal_account=account,
        requested_fields_json=sorted(changes),
        proposed_values_json={
            field: changes[field]
            for field in ("mobile_number", "email", "registered_address")
            if field in changes
        },
        reason=reason.strip(),
        identity_change_request=identity_change,
    )
    correction.evidence_documents.set(documents)
    _audit(
        correction=correction,
        actor=user,
        action="portal.kyc_correction.submitted",
        metadata={"requested_fields": sorted(changes), "evidence_count": len(documents)},
        request_metadata=request_metadata,
    )
    record_workflow_event(
        actor=user,
        workflow_name="portal_kyc_correction",
        entity_type="kyc_correction_request",
        entity_id=correction.pk,
        from_state="",
        to_state=KycCorrectionRequest.STATUS_SUBMITTED,
        trigger_reason="borrower_submitted_correction",
    )
    return serialize_portal(correction)


def list_for_portal(*, user, member):
    account = portal_account_for(user=user, member=member)
    return [
        serialize_portal(row)
        for row in KycCorrectionRequest.objects.filter(
            member=member, portal_account=account
        )
        .select_related("identity_change_request")
        .prefetch_related("evidence_documents")
    ]


def get_for_staff(*, actor, correction_id, for_update=False):
    queryset = KycCorrectionRequest.objects.select_related(
        "member", "identity_change_request", "reviewed_by_user"
    ).prefetch_related("evidence_documents")
    if for_update:
        queryset = queryset.select_for_update()
    correction = queryset.filter(pk=correction_id).first()
    if correction is None:
        return None
    access = evaluate_member_authority(
        actor_user=actor,
        member=correction.member,
        permission=member_services.MEMBER_UPDATE_PERMISSION,
    )
    if not access.allowed:
        if access.reason == "missing_permission":
            raise PermissionError("Member update authority is required.")
        raise MemberObjectAccessDenied("You cannot access this member.")
    return correction


def list_for_staff(*, actor):
    from sfpcl_credit.identity.modules import auth_service
    from sfpcl_credit.members.modules.member_authority import member_scope_predicate

    if member_services.MEMBER_UPDATE_PERMISSION not in auth_service.effective_permission_codes(
        actor
    ):
        raise PermissionError("Member update authority is required.")
    allowed_members = Member.objects.filter(
        member_scope_predicate(
            actor_user=actor, permission=member_services.MEMBER_UPDATE_PERMISSION
        )
    )
    return [
        serialize_staff(row)
        for row in KycCorrectionRequest.objects.filter(member__in=allowed_members)
        .select_related("member", "identity_change_request", "reviewed_by_user")
        .prefetch_related("evidence_documents")
    ]


@transaction.atomic
def start_review(*, actor, correction_id, internal_notes, request_metadata):
    correction = get_for_staff(actor=actor, correction_id=correction_id, for_update=True)
    if correction is None:
        return None
    if correction.status != KycCorrectionRequest.STATUS_SUBMITTED:
        raise KycCorrectionConflict("Only submitted corrections can enter review.")
    correction.status = KycCorrectionRequest.STATUS_UNDER_REVIEW
    correction.reviewed_by_user = actor
    correction.review_started_at = timezone.now()
    correction.internal_notes = str(internal_notes or "").strip()
    profile = KycProfile.objects.filter(
        party_type="member", party_id=correction.member_id
    ).first()
    if profile is None:
        raise ValidationError({"member": "The member KYC profile is unavailable."})
    for document in correction.evidence_documents.all():
        upload_audit = (
            AuditLog.objects.filter(
                action="portal.kyc_correction.evidence_uploaded",
                entity_id=document.pk,
                actor_user=correction.portal_account.user,
            )
            .order_by("-created_at", "-audit_log_id")
            .first()
        )
        metadata = upload_audit.new_value_json if upload_audit else {}
        document_type = metadata.get("document_type")
        if document_type not in ALLOWED_DOCUMENT_TYPES:
            raise ValidationError({"evidence": "KYC evidence provenance is incomplete."})
        KycDocument.objects.get_or_create(
            kyc_profile=profile,
            document_file=document,
            defaults={
                "document_type": document_type,
                "self_attested_flag": bool(metadata.get("self_attested_flag")),
                "verification_status": "pending",
            },
        )
    correction.save(
        update_fields=[
            "status",
            "reviewed_by_user",
            "review_started_at",
            "internal_notes",
            "updated_at",
        ]
    )
    _staff_event(
        correction=correction,
        actor=actor,
        action="members.kyc_correction.review_started",
        from_state=KycCorrectionRequest.STATUS_SUBMITTED,
        to_state=KycCorrectionRequest.STATUS_UNDER_REVIEW,
        request_metadata=request_metadata,
    )
    return serialize_staff(correction)


@transaction.atomic
def approve(*, actor, correction_id, request_metadata):
    correction = get_for_staff(actor=actor, correction_id=correction_id, for_update=True)
    if correction is None:
        return None
    if correction.status != KycCorrectionRequest.STATUS_UNDER_REVIEW:
        raise KycCorrectionConflict("Only corrections under review can be approved.")
    if correction.reviewed_by_user_id != actor.pk:
        raise PermissionError("Only the assigned reviewer can decide this correction.")
    evidence_ids = correction.evidence_documents.values_list("pk", flat=True)
    verified_count = KycDocument.objects.filter(
        kyc_profile__party_type="member",
        kyc_profile__party_id=correction.member_id,
        document_file_id__in=evidence_ids,
        verification_status="verified",
        verified_by_user__isnull=False,
    ).count()
    if verified_count != correction.evidence_documents.count():
        raise KycCorrectionConflict(
            "Every correction evidence document requires governed KYC verification."
        )
    identity_fields = {"pan", "aadhaar"} & set(correction.requested_fields_json)
    if identity_fields:
        MemberRegistry.approve_identity_change(correction.identity_change_request_id, actor)
    if correction.proposed_values_json:
        correction.member.refresh_from_db()
        MemberRegistry.update(
            correction.member_id,
            {
                **correction.proposed_values_json,
                "version": correction.member.version,
            },
            actor,
            request_ip_value=request_metadata.get("ip_address", ""),
            request_user_agent_value=request_metadata.get("user_agent", ""),
        )
    if not identity_fields:
        identity_change = correction.identity_change_request
        identity_change.status = "approved"
        identity_change.approver_user = actor
        identity_change.approved_at = timezone.now()
        identity_change.save(
            update_fields=["status", "approver_user", "approved_at"]
        )
        Member.objects.filter(pk=correction.member_id).update(
            kyc_status="pending", rekyc_due_date=None
        )
    KycProfile.objects.filter(
        party_type="member", party_id=correction.member_id
    ).update(
        kyc_status="pending",
        rekyc_due_date=None,
        rejection_reason=None,
        updated_at=timezone.now(),
    )
    from sfpcl_credit.compliance.models import KYCReview

    correction.kyc_review = (
        KYCReview.objects.filter(member=correction.member)
        .exclude(status=KYCReview.STATUS_COMPLETED)
        .order_by("-due_date", "-kyc_review_id")
        .first()
    )
    correction.status = KycCorrectionRequest.STATUS_APPROVED
    correction.decided_at = timezone.now()
    correction.save(
        update_fields=["kyc_review", "status", "decided_at", "updated_at"]
    )
    _staff_event(
        correction=correction,
        actor=actor,
        action="members.kyc_correction.approved",
        from_state=KycCorrectionRequest.STATUS_UNDER_REVIEW,
        to_state=KycCorrectionRequest.STATUS_APPROVED,
        request_metadata=request_metadata,
    )
    return serialize_staff(correction)


@transaction.atomic
def reject(*, actor, correction_id, rejection_reason, request_metadata):
    correction = get_for_staff(actor=actor, correction_id=correction_id, for_update=True)
    if correction is None:
        return None
    if correction.status != KycCorrectionRequest.STATUS_UNDER_REVIEW:
        raise KycCorrectionConflict("Only corrections under review can be rejected.")
    if correction.reviewed_by_user_id != actor.pk:
        raise PermissionError("Only the assigned reviewer can decide this correction.")
    if not isinstance(rejection_reason, str) or not rejection_reason.strip():
        raise ValidationError(
            {"rejection_reason": "A borrower-visible rejection reason is required."}
        )
    identity_change = correction.identity_change_request
    identity_change.status = "rejected"
    identity_change.save(update_fields=["status"])
    correction.status = KycCorrectionRequest.STATUS_REJECTED
    correction.rejection_reason = rejection_reason.strip()
    correction.decided_at = timezone.now()
    correction.save(
        update_fields=["status", "rejection_reason", "decided_at", "updated_at"]
    )
    _staff_event(
        correction=correction,
        actor=actor,
        action="members.kyc_correction.rejected",
        from_state=KycCorrectionRequest.STATUS_UNDER_REVIEW,
        to_state=KycCorrectionRequest.STATUS_REJECTED,
        request_metadata=request_metadata,
    )
    return serialize_staff(correction)


def serialize_staff(correction):
    return {
        **serialize_portal(correction),
        "member_id": str(correction.member_id),
        "member_name": correction.member.display_name,
        "internal_notes": correction.internal_notes,
        "reviewed_by_user_id": (
            str(correction.reviewed_by_user_id) if correction.reviewed_by_user_id else None
        ),
        "kyc_review_id": str(correction.kyc_review_id) if correction.kyc_review_id else None,
        "kyc_documents": [
            {
                "kyc_document_id": str(document.pk),
                "document_id": str(document.document_file_id),
                "document_type": document.document_type,
                "verification_status": document.verification_status,
            }
            for document in KycDocument.objects.filter(
                kyc_profile__party_type="member",
                kyc_profile__party_id=correction.member_id,
                document_file__in=correction.evidence_documents.all(),
            ).order_by("created_at", "kyc_document_id")
        ],
        "available_actions": (
            ["approve", "reject"]
            if correction.status == KycCorrectionRequest.STATUS_UNDER_REVIEW
            else ["review"]
            if correction.status == KycCorrectionRequest.STATUS_SUBMITTED
            else []
        ),
    }


def serialize_portal(correction):
    identity_change = correction.identity_change_request
    changes = {}
    if "pan" in correction.requested_fields_json:
        changes["pan"] = mask_protected_identity(identity_change.proposed_pan_encrypted, 10)
    if "aadhaar" in correction.requested_fields_json:
        changes["aadhaar"] = mask_protected_identity(
            identity_change.proposed_aadhaar_encrypted, 12
        )
    for field, value in correction.proposed_values_json.items():
        changes[field] = (
            ", ".join(str(part) for part in value.values() if part)
            if isinstance(value, dict)
            else str(value)
        )
    return {
        "kyc_correction_request_id": str(correction.pk),
        "status": correction.status,
        "changes": changes,
        "reason": correction.reason,
        "rejection_reason": correction.rejection_reason or None,
        "submitted_at": _timestamp(correction.submitted_at),
        "review_started_at": _timestamp(correction.review_started_at),
        "decided_at": _timestamp(correction.decided_at),
        "evidence": [
            {
                "document_id": str(document.pk),
                "file_name": document.file_name,
                "mime_type": document.mime_type,
                "uploaded_at": _timestamp(document.uploaded_at),
            }
            for document in correction.evidence_documents.all()
        ],
    }


def _audit(*, correction, actor, action, metadata, request_metadata):
    return AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account" if action.startswith("portal.") else "user",
        action=action,
        entity_type="kyc_correction_request",
        entity_id=correction.pk,
        new_value_json={
            "member_id": str(correction.member_id),
            "outcome": "accepted",
            **metadata,
        },
        ip_address=request_metadata.get("ip_address", ""),
        user_agent=request_metadata.get("user_agent", ""),
    )


def _staff_event(
    *, correction, actor, action, from_state, to_state, request_metadata
):
    _audit(
        correction=correction,
        actor=actor,
        action=action,
        metadata={"from_status": from_state, "to_status": to_state},
        request_metadata=request_metadata,
    )
    record_workflow_event(
        actor=actor,
        workflow_name="portal_kyc_correction",
        entity_type="kyc_correction_request",
        entity_id=correction.pk,
        from_state=from_state,
        to_state=to_state,
        trigger_reason=action,
    )


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z") if value else None


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": exc.messages[0] if getattr(exc, "messages", None) else str(exc)}
