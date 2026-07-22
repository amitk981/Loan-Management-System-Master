"""Security-return aggregate owner and security-instrument coordination interface."""

import hashlib
import json
import uuid

from django.db import models, transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.closure.models import (
    LoanClosure,
    ClosureRequirement,
    SecurityReturn,
    SecurityReturnItem,
    SecurityReturnRequest,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.security_instruments.models import SecurityPackage
from sfpcl_credit.security_instruments.modules.release_tracking import (
    ReleaseSourceUnavailable,
    resolve_release_sources,
    validate_release_result,
)


RECORD_PERMISSION = "closure.security_return.record"
RECORD_ROLES = {"company_secretary", "compliance_team_member"}


class SecurityReturnPermissionDenied(Exception):
    pass


class SecurityReturnNotFound(Exception):
    pass


class SecurityReturnValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class SecurityReturnConflict(Exception):
    pass


def record_security_return(
    *, actor, loan_closure_id, payload, idempotency_key, request=None
):
    try:
        _require_record_authority(actor)
        cleaned = _validate_request(payload, idempotency_key)
        scoped_closure = (
            LoanClosure.objects.select_related("loan_account__loan_application")
            .filter(pk=loan_closure_id)
            .first()
        )
        if scoped_closure is not None and not _has_record_scope(actor, scoped_closure):
            _audit_denied(
                actor=actor,
                loan_closure_id=loan_closure_id,
                reason="loan_closure_scope_denied",
                request=request,
            )
            raise SecurityReturnNotFound
    except SecurityReturnPermissionDenied:
        _audit_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="security_return_authority_denied",
            request=request,
        )
        raise
    except SecurityReturnValidation:
        _audit_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason="request_validation_failed",
            request=request,
        )
        raise
    payload_digest = _digest(
        {"loan_closure_id": str(loan_closure_id), "payload": cleaned["payload"]}
    )
    try:
        return _record_locked(
            actor=actor,
            loan_closure_id=loan_closure_id,
            cleaned=cleaned,
            payload_digest=payload_digest,
            request=request,
        )
    except (
        SecurityReturnConflict,
        SecurityReturnValidation,
        SecurityReturnNotFound,
    ) as exc:
        _audit_denied(
            actor=actor,
            loan_closure_id=loan_closure_id,
            reason=(
                "security_return_conflict"
                if isinstance(exc, SecurityReturnConflict)
                else (
                    "loan_closure_not_found"
                    if isinstance(exc, SecurityReturnNotFound)
                    else "request_validation_failed"
                )
            ),
            request=request,
        )
        raise


@transaction.atomic
def _record_locked(*, actor, loan_closure_id, cleaned, payload_digest, request):
    closure = (
        LoanClosure.objects.select_for_update()
        .select_related("loan_account")
        .filter(pk=loan_closure_id)
        .first()
    )
    if closure is None:
        raise SecurityReturnNotFound
    replay = SecurityReturnRequest.objects.select_related("security_return").filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if replay is not None:
        if replay.payload_digest != payload_digest:
            raise SecurityReturnConflict(
                "The idempotency key was already used for a different security-return request."
            )
        return _serialize(replay.security_return, replay=True)
    if (
        closure.closure_stage != LoanClosure.STAGE_FINANCIALLY_CLOSED
        or closure.loan_account.loan_account_status != "closed"
    ):
        raise SecurityReturnConflict(
            "Security return can be recorded only after financial closure."
        )
    existing = SecurityReturn.objects.filter(loan_closure=closure).first()
    if existing is not None:
        return _transition_existing(
            aggregate=existing,
            actor=actor,
            closure=closure,
            cleaned=cleaned,
            payload_digest=payload_digest,
            request=request,
        )

    package = SecurityPackage.objects.filter(
        loan_application_id=closure.loan_account.loan_application_id
    ).first()
    applicability = _derive_applicability(package)
    try:
        sources = (
            resolve_release_sources(package=package, for_update=True)
            if package is not None
            else {item_type: None for item_type in SecurityReturnItem.TYPES}
        )
    except ReleaseSourceUnavailable as exc:
        raise SecurityReturnConflict(str(exc)) from exc
    item_values, acknowledgement = _resolve_item_values(
        closure=closure,
        package=package,
        sources=sources,
        applicability=applicability,
        payload=cleaned["payload"],
        actor=actor,
        expected_version=0,
    )
    now = timezone.now()
    aggregate_id = uuid.uuid4()
    all_not_applicable = not any(applicability.values())
    all_complete = all(
        not applicability[item_type]
        or item_values[item_type]["status"] in {"returned", "released", "completed"}
        for item_type in SecurityReturnItem.TYPES
    )
    aggregate_status = (
        SecurityReturn.STATUS_COMPLETED
        if all_not_applicable or (all_complete and acknowledgement is not None)
        else SecurityReturn.STATUS_PENDING
    )
    role = _record_role(actor)
    aggregate_audit = AuditLog.objects.create(
        actor_user=actor,
        action="closure.security_return.recorded",
        entity_type="security_return",
        entity_id=aggregate_id,
        old_value_json=None,
        new_value_json={
            "loan_closure_id": str(closure.pk),
            "security_package_id": str(package.pk) if package else None,
            "status": aggregate_status,
            "applicability": applicability,
            "recorded_by_role_code": role,
            "idempotency_key_digest": cleaned["idempotency_key_digest"],
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    aggregate = SecurityReturn.objects.create(
        security_return_id=aggregate_id,
        loan_closure=closure,
        security_package=package,
        return_status=aggregate_status,
        version=1,
        recorded_by_user=actor,
        recorded_by_role_code=role,
        recorded_at=now,
        completed_at=(now if aggregate_status == SecurityReturn.STATUS_COMPLETED else None),
        acknowledgement_document=acknowledgement,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        record_audit=aggregate_audit,
    )
    for item_type in SecurityReturnItem.TYPES:
        item_id = uuid.uuid4()
        values = item_values[item_type]
        status = values["status"]
        audit = AuditLog.objects.create(
            actor_user=actor,
            action="closure.security_return.item_transitioned",
            entity_type="security_return_item",
            entity_id=item_id,
            old_value_json=None,
            new_value_json={
                "security_return_id": str(aggregate.pk),
                "item_type": item_type,
                "status": status,
            },
            ip_address=request_ip(request) if request else "",
            user_agent=request_user_agent(request) if request else "",
        )
        SecurityReturnItem.objects.create(
            security_return_item_id=item_id,
            security_return=aggregate,
            item_type=item_type,
            item_status=status,
            source_item_id=(sources[item_type].pk if sources[item_type] else None),
            custody_location=values.get("custody_location"),
            returned_released_by_user=(
                actor if status in {"returned", "released"} else None
            ),
            returned_released_to=values.get("returned_released_to"),
            returned_released_at=values.get("returned_released_at"),
            pending_reason=values.get("pending_reason"),
            acknowledgement_document=(
                acknowledgement if status in {"returned", "released"} else None
            ),
            psn=values.get("psn"),
            urf_document=values.get("urf_document"),
            urf_date=values.get("urf_date"),
            unpledge_type=values.get("unpledge_type"),
            pledgor_dp_submitted_at=values.get("pledgor_dp_submitted_at"),
            pledgee_dp_acted_at=values.get("pledgee_dp_acted_at"),
            pledgee_dp_outcome=values.get("pledgee_dp_outcome"),
            auto_unpledge_flag=values.get("auto_unpledge_flag"),
            completion_evidence_document=values.get("completion_evidence_document"),
            completed_at=values.get("completed_at"),
            transition_audit=audit,
        )
        if item_type == "cdsl" and applicability[item_type]:
            _audit_cdsl_result(
                actor=actor,
                aggregate=aggregate,
                item_values=values,
                source=sources[item_type],
                request=request,
            )
    SecurityReturnRequest.objects.create(
        security_return=aggregate,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        resulting_version=aggregate.version,
    )
    if aggregate_status == SecurityReturn.STATUS_COMPLETED and package is not None:
        ClosureRequirement.complete_security_return_requirement(
            loan_closure_id=closure.pk
        )
    return _serialize(aggregate, replay=False)


def _transition_existing(
    *, aggregate, actor, closure, cleaned, payload_digest, request
):
    if aggregate.return_status == SecurityReturn.STATUS_COMPLETED:
        raise SecurityReturnConflict("The security return is already complete.")
    package = aggregate.security_package
    applicability = _derive_applicability(package)
    try:
        sources = resolve_release_sources(package=package, for_update=True)
    except ReleaseSourceUnavailable as exc:
        raise SecurityReturnConflict(str(exc)) from exc
    values, new_acknowledgement = _resolve_item_values(
        closure=closure,
        package=package,
        sources=sources,
        applicability=applicability,
        payload=cleaned["payload"],
        actor=actor,
        expected_version=aggregate.version,
    )
    supplied_types = {
        item["item_type"] for item in cleaned["payload"].get("items", [])
    }
    retained_items = {item.item_type: item for item in aggregate.items.all()}
    for item_type in supplied_types:
        retained = retained_items[item_type]
        if retained.item_status == "rejected" or retained.item_status in {
            "returned",
            "released",
            "completed",
        }:
            raise SecurityReturnConflict(
                f"The {item_type} result is terminal and cannot be changed."
            )
        item_values = values[item_type]
        AuditLog.objects.create(
            actor_user=actor,
            action="closure.security_return.item_transitioned",
            entity_type="security_return_item",
            entity_id=retained.pk,
            old_value_json={"status": retained.item_status},
            new_value_json={"status": item_values["status"]},
            ip_address=request_ip(request) if request else "",
            user_agent=request_user_agent(request) if request else "",
        )
        models_values = _item_update_values(
            item_values=item_values,
            actor=actor,
            acknowledgement=(new_acknowledgement or aggregate.acknowledgement_document),
        )
        models.QuerySet.update(
            SecurityReturnItem.objects.filter(pk=retained.pk), **models_values
        )
        if item_type == "cdsl":
            _audit_cdsl_result(
                actor=actor,
                aggregate=aggregate,
                item_values=item_values,
                source=sources[item_type],
                request=request,
            )
    aggregate.refresh_from_db()
    current_items = list(aggregate.items.all())
    acknowledgement = new_acknowledgement or aggregate.acknowledgement_document
    completed = bool(acknowledgement) and all(
        item.item_status in {"not_applicable", "returned", "released", "completed"}
        for item in current_items
    )
    next_version = aggregate.version + 1
    models.QuerySet.update(
        SecurityReturn.objects.filter(pk=aggregate.pk, version=aggregate.version),
        version=next_version,
        return_status=(
            SecurityReturn.STATUS_COMPLETED if completed else SecurityReturn.STATUS_PENDING
        ),
        completed_at=timezone.now() if completed else None,
        acknowledgement_document=acknowledgement,
    )
    aggregate.refresh_from_db()
    SecurityReturnRequest.objects.create(
        security_return=aggregate,
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=payload_digest,
        resulting_version=aggregate.version,
    )
    if completed:
        ClosureRequirement.complete_security_return_requirement(
            loan_closure_id=closure.pk
        )
    return _serialize(aggregate, replay=False)


def _item_update_values(*, item_values, actor, acknowledgement):
    status = item_values["status"]
    return {
        "item_status": status,
        "custody_location": item_values.get("custody_location"),
        "returned_released_by_user": actor if status in {"returned", "released"} else None,
        "returned_released_to": item_values.get("returned_released_to"),
        "returned_released_at": item_values.get("returned_released_at"),
        "pending_reason": item_values.get("pending_reason"),
        "acknowledgement_document": (
            acknowledgement if status in {"returned", "released"} else None
        ),
        "psn": item_values.get("psn"),
        "urf_document": item_values.get("urf_document"),
        "urf_date": item_values.get("urf_date"),
        "unpledge_type": item_values.get("unpledge_type"),
        "pledgor_dp_submitted_at": item_values.get("pledgor_dp_submitted_at"),
        "pledgee_dp_acted_at": item_values.get("pledgee_dp_acted_at"),
        "pledgee_dp_outcome": item_values.get("pledgee_dp_outcome"),
        "auto_unpledge_flag": item_values.get("auto_unpledge_flag"),
        "completion_evidence_document": item_values.get("completion_evidence_document"),
        "completed_at": item_values.get("completed_at"),
    }


def _audit_cdsl_result(*, actor, aggregate, item_values, source, request):
    AuditLog.objects.create(
        actor_user=actor,
        action="security.cdsl_unpledge.result_recorded",
        entity_type="cdsl_share_pledge",
        entity_id=source.pk,
        old_value_json=None,
        new_value_json={
            "security_return_id": str(aggregate.pk),
            "psn": item_values.get("psn") or source.pledge_sequence_number,
            "outcome": item_values["status"],
            "unpledge_type": item_values.get("unpledge_type"),
            "pledgee_dp_outcome": item_values.get("pledgee_dp_outcome"),
            "auto_unpledge_flag": item_values.get("auto_unpledge_flag"),
            "urf_document_id": (
                str(item_values["urf_document"].pk)
                if item_values.get("urf_document")
                else None
            ),
            "completion_evidence_document_id": (
                str(item_values["completion_evidence_document"].pk)
                if item_values.get("completion_evidence_document")
                else None
            ),
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _derive_applicability(package):
    if package is None:
        return {item_type: False for item_type in SecurityReturnItem.TYPES}
    return {
        "sh4": package.physical_share_security_required_flag,
        "blank_cheque": package.blank_cheque_required_flag,
        "poa": package.poa_required_flag,
        "cdsl": package.demat_pledge_required_flag,
    }


def _validate_request(payload, idempotency_key):
    if not isinstance(payload, dict):
        raise SecurityReturnValidation({"body": ["Expected a JSON object."]})
    allowed = {
        "security_package_id",
        "expected_version",
        "acknowledgement_document_id",
        "items",
    }
    unknown = set(payload) - allowed
    if unknown:
        raise SecurityReturnValidation(
            {
                key: ["Applicability and security-return facts are server-derived."]
                for key in sorted(unknown)
            }
        )
    key = (idempotency_key or "").strip()
    if not key:
        raise SecurityReturnValidation(
            {"idempotency_key": ["Idempotency-Key header is required."]}
        )
    return {"payload": payload, "idempotency_key_digest": _digest(key)}


def _resolve_item_values(
    *, closure, package, sources, applicability, payload, actor, expected_version
):
    if package is None:
        if payload:
            raise SecurityReturnValidation(
                {"security_package_id": ["This closure has no security package."]}
            )
        return (
            {
                item_type: {"status": "not_applicable"}
                for item_type in SecurityReturnItem.TYPES
            },
            None,
        )
    if str(payload.get("security_package_id", "")) != str(package.pk):
        raise SecurityReturnValidation(
            {"security_package_id": ["Must match the closure's security package."]}
        )
    if payload.get("expected_version") != expected_version:
        raise SecurityReturnConflict("The security-return version is stale.")
    items = payload.get("items")
    if not isinstance(items, list):
        raise SecurityReturnValidation({"items": ["Expected a list of item results."]})
    supplied = {}
    for item in items:
        if (
            not isinstance(item, dict)
            or item.get("item_type") not in SecurityReturnItem.TYPES
        ):
            raise SecurityReturnValidation(
                {"items": ["Each item must name a supported item_type."]}
            )
        item_type = item["item_type"]
        if item_type in supplied:
            raise SecurityReturnValidation({"items": [f"Duplicate {item_type} result."]})
        if not applicability[item_type]:
            raise SecurityReturnValidation(
                {"items": [f"{item_type} is not applicable to this security package."]}
            )
        if str(item.get("source_item_id", "")) != str(sources[item_type].pk):
            raise SecurityReturnValidation(
                {"items": [f"{item_type} source identity does not match its owner."]}
            )
        supplied[item_type] = item
    acknowledgement = _resolve_document(
        closure=closure,
        document_id=payload.get("acknowledgement_document_id"),
        required=False,
        field="acknowledgement_document_id",
    )
    resolved = {}
    for item_type in SecurityReturnItem.TYPES:
        if not applicability[item_type]:
            resolved[item_type] = {"status": "not_applicable"}
            continue
        item = supplied.get(item_type)
        if item is None:
            if expected_version == 0:
                raise SecurityReturnValidation(
                    {"items": [f"A result is required for applicable {item_type}."]}
                )
            resolved[item_type] = {
                "status": "pending",
                "pending_reason": "Retained from the previous request.",
            }
            continue
        outcome = item.get("outcome")
        try:
            owner = validate_release_result(
                item_type=item_type, source=sources[item_type], outcome=outcome
            )
        except ReleaseSourceUnavailable as exc:
            raise SecurityReturnValidation({"items": [str(exc)]}) from exc
        values = {"status": outcome, **owner}
        if outcome == "pending":
            reason = str(item.get("pending_reason") or "").strip()
            if not reason:
                raise SecurityReturnValidation(
                    {"items": [f"{item_type} pending_reason is required."]}
                )
            values["pending_reason"] = reason
        elif item_type == "cdsl":
            _resolve_cdsl_values(
                values=values,
                item=item,
                closure=closure,
                source=sources[item_type],
                outcome=outcome,
            )
        else:
            recipient = str(item.get("returned_released_to") or "").strip()
            occurred_at = parse_datetime(str(item.get("returned_released_at") or ""))
            if not recipient or occurred_at is None or acknowledgement is None:
                raise SecurityReturnValidation(
                    {
                        "items": [
                            f"{item_type} completion requires recipient, time, "
                            "and acknowledgement."
                        ]
                    }
                )
            values.update(
                returned_released_to=recipient,
                returned_released_at=occurred_at,
            )
        resolved[item_type] = values
    return resolved, acknowledgement


def _resolve_cdsl_values(*, values, item, closure, source, outcome):
    if item.get("psn") != source.pledge_sequence_number:
        raise SecurityReturnValidation(
            {"items": ["CDSL PSN must match the owned pledge identity."]}
        )
    urf_document = _resolve_document(
        closure=closure,
        document_id=item.get("urf_document_id"),
        required=True,
        field="urf_document_id",
    )
    completion_document = _resolve_document(
        closure=closure,
        document_id=item.get("completion_evidence_document_id"),
        required=(outcome == "completed"),
        field="completion_evidence_document_id",
    )
    urf_date = parse_date(str(item.get("urf_date") or ""))
    unpledge_type = item.get("unpledge_type")
    pledgor_submitted = parse_datetime(str(item.get("pledgor_dp_submitted_at") or ""))
    pledgee_acted = parse_datetime(str(item.get("pledgee_dp_acted_at") or ""))
    completed_at = parse_datetime(str(item.get("completed_at") or ""))
    dp_outcome = item.get("pledgee_dp_outcome")
    auto_flag = item.get("auto_unpledge_flag")
    errors = []
    if urf_date is None:
        errors.append("CDSL URF date is required.")
    if unpledge_type not in {"partial", "full"}:
        errors.append("CDSL unpledge_type must be partial or full.")
    if pledgor_submitted is None or pledgee_acted is None:
        errors.append("Both CDSL DP timestamps are required.")
    elif pledgee_acted < pledgor_submitted:
        errors.append("Pledgee DP action cannot predate pledgor DP submission.")
    expected_dp_outcome = "accepted" if outcome == "completed" else "rejected"
    if dp_outcome != expected_dp_outcome:
        errors.append(f"A {outcome} CDSL result requires DP outcome {expected_dp_outcome}.")
    if not isinstance(auto_flag, bool):
        errors.append("CDSL auto_unpledge_flag is required.")
    if outcome == "completed" and completed_at is None:
        errors.append("CDSL completion time is required.")
    if outcome == "rejected" and completed_at is not None:
        errors.append("A rejected CDSL action cannot carry a completion time.")
    if completed_at and pledgee_acted and completed_at < pledgee_acted:
        errors.append("CDSL completion cannot predate the pledgee DP action.")
    if errors:
        raise SecurityReturnValidation({"items": errors})
    values.update(
        psn=source.pledge_sequence_number,
        urf_document=urf_document,
        urf_date=urf_date,
        unpledge_type=unpledge_type,
        pledgor_dp_submitted_at=pledgor_submitted,
        pledgee_dp_acted_at=pledgee_acted,
        pledgee_dp_outcome=dp_outcome,
        auto_unpledge_flag=auto_flag,
        completion_evidence_document=completion_document,
        completed_at=completed_at,
    )


def _resolve_document(*, closure, document_id, required, field):
    if not document_id:
        if required:
            raise SecurityReturnValidation({field: ["This evidence document is required."]})
        return None
    from sfpcl_credit.legal_documents.models import LoanDocument

    loan_document = (
        LoanDocument.objects.select_related("document")
        .filter(
            loan_application_id=closure.loan_account.loan_application_id,
            document_id=document_id,
            verification_status="verified",
        )
        .first()
    )
    if loan_document is None or loan_document.document.sensitivity_level not in {
        "confidential",
        "restricted",
    }:
        raise SecurityReturnValidation(
            {field: ["Must reference verified restricted evidence for this loan."]}
        )
    return loan_document.document


def _require_record_authority(actor):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or RECORD_PERMISSION not in permissions
        or not roles.intersection(RECORD_ROLES)
    ):
        raise SecurityReturnPermissionDenied


def _record_role(actor):
    roles = set(auth_service.effective_role_codes(actor))
    return (
        "company_secretary"
        if "company_secretary" in roles
        else "compliance_team_member"
    )


def _has_record_scope(actor, closure):
    roles = set(auth_service.effective_role_codes(actor))
    application = closure.loan_account.loan_application
    if application.application_status != application.STATUS_APPROVED_BY_SANCTION:
        return False
    if (
        closure.loan_account.loan_account_status != "closed"
        or closure.loan_account.closed_at != closure.closed_at
    ):
        return False
    if "company_secretary" in roles:
        return True
    return bool(
        "compliance_team_member" in roles and "compliance" in actor.team_codes()
    )


@transaction.atomic
def _audit_denied(*, actor, loan_closure_id, reason, request):
    if not getattr(actor, "pk", None):
        return
    AuditLog.objects.create(
        actor_user=actor,
        action="closure.security_return.denied",
        entity_type="loan_closure",
        entity_id=loan_closure_id,
        old_value_json=None,
        new_value_json={"reason": reason},
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _serialize(aggregate, *, replay):
    items = aggregate.items.order_by("security_return_item_id")
    item_map = {item.item_type: item for item in items}
    cdsl_source = None
    cdsl_item = item_map.get("cdsl")
    if cdsl_item and cdsl_item.source_item_id:
        from sfpcl_credit.security_instruments.models import CDSLSharePledge

        cdsl_source = CDSLSharePledge.objects.filter(pk=cdsl_item.source_item_id).first()
    return {
        "security_return_id": str(aggregate.pk),
        "loan_closure_id": str(aggregate.loan_closure_id),
        "security_package_id": (
            str(aggregate.security_package_id)
            if aggregate.security_package_id
            else None
        ),
        "status": aggregate.return_status,
        "version": aggregate.version,
        "completed_at": (
            aggregate.completed_at.isoformat().replace("+00:00", "Z")
            if aggregate.completed_at
            else None
        ),
        "items": [
            {
                "item_type": item_type,
                "status": item_map[item_type].item_status,
                "source_item_id": (
                    str(item_map[item_type].source_item_id)
                    if item_map[item_type].source_item_id
                    else None
                ),
                "custody_location": item_map[item_type].custody_location,
                "returned_released_to": item_map[item_type].returned_released_to,
                **(
                    {
                        "psn": item_map[item_type].psn,
                        "urf_date": (
                            item_map[item_type].urf_date.isoformat()
                            if item_map[item_type].urf_date
                            else None
                        ),
                        "unpledge_type": item_map[item_type].unpledge_type,
                        "pledgor_dp_submitted_at": _iso(
                            item_map[item_type].pledgor_dp_submitted_at
                        ),
                        "pledgee_dp_acted_at": _iso(
                            item_map[item_type].pledgee_dp_acted_at
                        ),
                        "pledgee_dp_outcome": item_map[item_type].pledgee_dp_outcome,
                        "auto_unpledge_flag": item_map[item_type].auto_unpledge_flag,
                        "completed_at": _iso(item_map[item_type].completed_at),
                        "pledgor_bo_account": (
                            f"************{cdsl_source.pledgor_bo_account_last4}"
                            if cdsl_source
                            else None
                        ),
                        "pledgee_bo_account": (
                            f"************{cdsl_source.pledgee_bo_account_last4}"
                            if cdsl_source and cdsl_source.pledgee_bo_account_last4
                            else None
                        ),
                    }
                    if item_type == "cdsl"
                    else {}
                ),
            }
            for item_type in SecurityReturnItem.TYPES
        ],
        "idempotency_replayed": replay,
        "available_actions": (
            []
            if aggregate.return_status == SecurityReturn.STATUS_COMPLETED
            else [RECORD_PERMISSION]
        ),
    }


def _digest(value):
    raw = value if isinstance(value, str) else json.dumps(
        value, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def _iso(value):
    return value.isoformat().replace("+00:00", "Z") if value else None
