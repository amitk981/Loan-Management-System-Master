import re
import uuid
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from math import ceil
from pathlib import PurePath
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.compliance.models import AuditObservation, ComplianceEvidence
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.shared.audit_text import UnsafeAuditText, safe_audit_text
from sfpcl_credit.workflows.models import WorkflowEvent


READ_PERMISSION = "audit.observation.read"
CREATE_PERMISSION = "audit.observation.create"
AUDIT_SCOPE = ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY
MAX_OBSERVATION_LENGTH = 2000
MAX_SOURCE_REFERENCES = 20
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
_LIST_PARAMS = {
    "page",
    "page_size",
    "audit_scope",
    "created_by_user_id",
    "created_from",
    "created_to",
}
_ACTIVE_CONTENT = re.compile(r"<[^>]+>|(?:javascript|data):", re.IGNORECASE)
_PAN_LIKE = re.compile(r"(?<![A-Z0-9])[A-Z]{5}\d{4}[A-Z](?![A-Z0-9])")


class ObservationDenied(PermissionError):
    pass


class ObservationMissing(LookupError):
    pass


class ObservationInvalid(ValueError):
    def __init__(self, field_errors):
        super().__init__("Audit observation request failed validation.")
        self.field_errors = field_errors


@dataclass(frozen=True)
class DocumentContent:
    body: bytes
    file_name: str
    mime_type: str


def require(actor, permission):
    permissions = set(auth_service.effective_permission_codes(actor))
    roles = set(auth_service.effective_role_codes(actor))
    if (
        not actor.can_authenticate()
        or "internal_auditor" not in roles
        or not has_active_audit_read_scope(actor)
        or permission not in permissions
    ):
        raise ObservationDenied


@transaction.atomic
def create(*, actor, payload, request):
    require(actor, CREATE_PERMISSION)
    allowed = {"audit_scope", "observation", "source_references"}
    unknown = set(payload) - allowed
    if unknown:
        raise ObservationInvalid(
            {field: "Unknown field." for field in sorted(unknown)}
        )
    if payload.get("audit_scope") != AUDIT_SCOPE:
        raise ObservationInvalid({"audit_scope": "Audit scope is invalid."})
    raw_observation = payload.get("observation")
    try:
        observation_text = safe_audit_text(
            raw_observation,
            max_length=MAX_OBSERVATION_LENGTH,
        )
    except UnsafeAuditText as exc:
        raise ObservationInvalid({"observation": str(exc)}) from exc
    if _ACTIVE_CONTENT.search(observation_text) or _PAN_LIKE.search(observation_text.upper()):
        raise ObservationInvalid(
            {"observation": "The observation contains unsafe or sensitive content."}
        )
    references = _resolve_references(
        actor=actor,
        value=payload.get("source_references"),
    )
    row = AuditObservation.objects.create(
        created_by_user=actor,
        created_by_full_name=actor.full_name,
        created_by_role_code=actor.primary_role.role_code,
        created_by_team_codes_json=actor.team_codes(),
        audit_scope=AUDIT_SCOPE,
        observation_text=observation_text,
        source_references_json=references,
    )
    from sfpcl_credit.api import request_ip, request_user_agent

    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="audit.observation.created",
        entity_type="audit_observation",
        entity_id=row.pk,
        new_value_json={
            "actor_role_codes": [row.created_by_role_code],
            "actor_team_codes": row.created_by_team_codes_json,
            "audit_scope": row.audit_scope,
            "source_references": row.source_references_json,
            "outcome": "success",
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return serialize(row, actor=actor)


def list_observations(*, actor, query):
    require(actor, READ_PERMISSION)
    unknown = set(query.keys()) - _LIST_PARAMS
    if unknown:
        raise ObservationInvalid(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int(query.get("page"), 1, field="page")
    page_size = min(
        _positive_int(
            query.get("page_size"),
            DEFAULT_PAGE_SIZE,
            field="page_size",
        ),
        MAX_PAGE_SIZE,
    )
    queryset = AuditObservation.objects.select_related("created_by_user").all()
    audit_scope = query.get("audit_scope")
    if audit_scope:
        if audit_scope != AUDIT_SCOPE:
            raise ObservationInvalid({"audit_scope": "Audit scope is invalid."})
        queryset = queryset.filter(audit_scope=audit_scope)
    creator_id = query.get("created_by_user_id")
    if creator_id:
        try:
            creator_id = uuid.UUID(str(creator_id))
        except (TypeError, ValueError):
            raise ObservationInvalid(
                {"created_by_user_id": "Source identifier is invalid."}
            ) from None
        queryset = queryset.filter(created_by_user_id=creator_id)
    created_from = _date_filter(query, "created_from")
    created_to = _date_filter(query, "created_to")
    if created_from and created_to and created_from > created_to:
        raise ObservationInvalid({"created_to": "Must be on or after created_from."})
    if created_from:
        queryset = queryset.filter(created_at__gte=_day_boundary(created_from))
    if created_to:
        queryset = queryset.filter(
            created_at__lt=_day_boundary(created_to + timedelta(days=1))
        )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return (
        [serialize(row, actor=actor) for row in queryset[offset : offset + page_size]],
        {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    )


def retrieve(*, actor, observation_id):
    require(actor, READ_PERMISSION)
    row = (
        AuditObservation.objects.select_related("created_by_user")
        .filter(pk=observation_id)
        .first()
    )
    if row is None:
        raise ObservationMissing
    return serialize(row, actor=actor)


def serialize(row, *, actor):
    return {
        "audit_observation_id": str(row.pk),
        "creator": {
            "user_id": str(row.created_by_user_id),
            "full_name": row.created_by_full_name,
            "role_code": row.created_by_role_code,
            "team_codes": row.created_by_team_codes_json,
        },
        "audit_scope": row.audit_scope,
        "observation": row.observation_text,
        "source_references": [
            _project_reference(reference, observation=row, actor=actor)
            for reference in row.source_references_json
        ],
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


@transaction.atomic
def read_evidence(*, actor, observation_id, evidence_id, token, request, storage=None):
    require(actor, READ_PERMISSION)
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        "reports.compliance.read" not in permissions
        or document_services.DOCUMENT_DOWNLOAD_PERMISSION not in permissions
    ):
        raise ObservationMissing
    observation = AuditObservation.objects.filter(pk=observation_id).first()
    if observation is None:
        raise ObservationMissing
    reference = next(
        (
            item
            for item in observation.source_references_json
            if item.get("source_type") == "compliance_evidence"
            and item.get("source_id") == str(evidence_id)
        ),
        None,
    )
    if reference is None:
        raise ObservationMissing
    evidence = (
        ComplianceEvidence.objects.select_related("document")
        .filter(pk=evidence_id)
        .first()
    )
    if evidence is None or str(evidence.document_id) != reference.get("document_id"):
        raise ObservationMissing
    scope = _evidence_scope(
        actor=actor,
        observation=observation,
        evidence=evidence,
    )
    try:
        body = document_services.read_with_download_capability(
            document=evidence.document,
            scope=scope,
            token=token,
            storage=storage or LocalDocumentStorage(),
        )
    except (ValidationError, ValueError, OSError) as exc:
        raise ObservationMissing from exc
    from sfpcl_credit.api import request_ip, request_user_agent

    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="audit.observation.evidence_accessed",
        entity_type="audit_observation",
        entity_id=observation.pk,
        new_value_json={
            "audit_scope": observation.audit_scope,
            "compliance_evidence_id": str(evidence.pk),
            "document_id": str(evidence.document_id),
            "sensitivity_level": evidence.document.sensitivity_level,
            "outcome": "success",
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return DocumentContent(
        body=body,
        file_name=_safe_evidence_file_name(evidence.document.file_name),
        mime_type=evidence.document.mime_type or "application/octet-stream",
    )


def _resolve_references(*, actor, value):
    if not isinstance(value, list) or not value:
        raise ObservationInvalid(
            {"source_references": "At least one source reference is required."}
        )
    if len(value) > MAX_SOURCE_REFERENCES:
        raise ObservationInvalid(
            {
                "source_references": (
                    f"No more than {MAX_SOURCE_REFERENCES} references are allowed."
                )
            }
        )
    resolved = []
    seen = set()
    for index, reference in enumerate(value):
        field = f"source_references.{index}"
        if not isinstance(reference, dict) or set(reference) != {
            "source_type",
            "source_id",
        }:
            raise ObservationInvalid({field: "Source reference is invalid."})
        try:
            source_id = uuid.UUID(str(reference["source_id"]))
        except (TypeError, ValueError):
            raise ObservationInvalid({field: "Source identifier is invalid."}) from None
        identity = (reference["source_type"], source_id)
        if identity in seen:
            raise ObservationInvalid({field: "Duplicate source reference."})
        seen.add(identity)
        if reference["source_type"] == "audit_log":
            if "audit.audit_log.read" not in auth_service.effective_permission_codes(actor):
                raise ObservationMissing
            source = AuditLog.objects.filter(pk=source_id).first()
            if source is None:
                raise ObservationMissing
            resolved.append(
                {
                    "source_type": "audit_log",
                    "source_id": str(source.pk),
                    "entity_type": source.entity_type,
                    "entity_id": str(source.entity_id) if source.entity_id else None,
                }
            )
            continue
        if reference["source_type"] == "workflow_event":
            if (
                "audit.workflow_event.read"
                not in auth_service.effective_permission_codes(actor)
            ):
                raise ObservationMissing
            source = WorkflowEvent.objects.filter(pk=source_id).first()
            if source is None:
                raise ObservationMissing
            resolved.append(
                {
                    "source_type": "workflow_event",
                    "source_id": str(source.pk),
                    "entity_type": source.entity_type,
                    "entity_id": str(source.entity_id),
                }
            )
            continue
        if reference["source_type"] == "version_history":
            if (
                "audit.version_history.read"
                not in auth_service.effective_permission_codes(actor)
            ):
                raise ObservationMissing
            source = VersionHistory.objects.filter(pk=source_id).first()
            if source is None:
                raise ObservationMissing
            resolved.append(
                {
                    "source_type": "version_history",
                    "source_id": str(source.pk),
                    "entity_type": source.versioned_entity_type,
                    "entity_id": str(source.versioned_entity_id),
                }
            )
            continue
        if reference["source_type"] == "compliance_evidence":
            permissions = set(auth_service.effective_permission_codes(actor))
            if "reports.compliance.read" not in permissions:
                raise ObservationMissing
            source = (
                ComplianceEvidence.objects.select_related("document")
                .filter(pk=source_id)
                .first()
            )
            if source is None:
                raise ObservationMissing
            resolved.append(
                {
                    "source_type": "compliance_evidence",
                    "source_id": str(source.pk),
                    "entity_type": source.source_entity_type,
                    "entity_id": str(source.source_entity_id),
                    "evidence_type": source.evidence_type,
                    "document_id": str(source.document_id),
                }
            )
            continue
        raise ObservationInvalid({field: "Source type is not supported."})
    return resolved


def _project_reference(reference, *, observation, actor):
    projected = {
        key: value
        for key, value in reference.items()
        if key != "document_id"
    }
    if reference.get("source_type") != "compliance_evidence":
        return projected
    evidence = (
        ComplianceEvidence.objects.select_related("document")
        .filter(
            pk=reference["source_id"],
            document_id=reference["document_id"],
        )
        .first()
    )
    permissions = set(auth_service.effective_permission_codes(actor))
    if evidence is None or "reports.compliance.read" not in permissions:
        raise ObservationMissing
    projected["evidence"] = {
        "document_id": str(evidence.document_id),
        "file_name": _safe_evidence_file_name(evidence.document.file_name),
        "sensitivity_level": evidence.document.sensitivity_level,
        "download_url": None,
        "expires_at": None,
    }
    if document_services.DOCUMENT_DOWNLOAD_PERMISSION not in permissions:
        return projected
    capability = document_services.issue_download_capability(
        document=evidence.document,
        scope=_evidence_scope(
            actor=actor,
            observation=observation,
            evidence=evidence,
        ),
    )
    path = (
        f"/api/v1/audit-observations/{observation.pk}/evidence/{evidence.pk}/download/"
    )
    projected["evidence"]["download_url"] = (
        f"{path}?{urlencode({'token': capability['token']})}"
    )
    projected["evidence"]["expires_at"] = capability["expires_at"]
    return projected


def _evidence_scope(*, actor, observation, evidence):
    return {
        "user_id": str(actor.pk),
        "audit_scope": observation.audit_scope,
        "audit_observation_id": str(observation.pk),
        "compliance_evidence_id": str(evidence.pk),
        "document_id": str(evidence.document_id),
    }


def _safe_evidence_file_name(value):
    name = PurePath(value or "").name
    try:
        safe_audit_text(name, max_length=255)
    except UnsafeAuditText:
        name = ""
    if name and not _ACTIVE_CONTENT.search(name) and not _PAN_LIKE.search(name.upper()):
        return name
    suffix = PurePath(value or "").suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
        suffix = ""
    return f"restricted-evidence{suffix}"


def _positive_int(value, default, *, field):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ObservationInvalid({field: "Must be a positive integer."}) from None
    if parsed < 1:
        raise ObservationInvalid({field: "Must be a positive integer."})
    return parsed


def _date_filter(query, field):
    raw = query.get(field)
    if not raw:
        return None
    try:
        value = parse_date(raw)
    except (TypeError, ValueError):
        value = None
    if value is None:
        raise ObservationInvalid({field: "Must be a valid ISO date."})
    return value


def _day_boundary(value):
    return timezone.make_aware(datetime.combine(value, time.min))
