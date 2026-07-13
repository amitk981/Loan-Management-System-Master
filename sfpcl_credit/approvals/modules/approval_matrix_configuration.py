import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from math import ceil

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.approvals.models import (
    ApprovalConfigurationLock,
    ApprovalConfigurationProposal,
    ApprovalMatrixRule,
    SanctionCommittee,
)
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service


READ_PERMISSION = "approvals.matrix.read"
MANAGE_PERMISSION = "approvals.matrix.manage"


class ConfigurationConflict(Exception):
    def __init__(self, message, code="CONFIGURATION_CONFLICT"):
        super().__init__(message)
        self.code = code


def can_read(user):
    return READ_PERMISSION in auth_service.effective_permission_codes(user)


def can_manage(user):
    return MANAGE_PERMISSION in auth_service.effective_permission_codes(user)


def serialize_rule(rule):
    return {
        "approval_matrix_rule_id": str(rule.pk), "decision_type": rule.decision_type,
        "amount_min": _decimal(rule.amount_min), "amount_max": _decimal(rule.amount_max),
        "condition_code": rule.condition_code,
        "required_approver_roles": list(rule.required_approver_roles_json),
        "required_director_count": rule.required_director_count,
        "joint_approval_required_flag": rule.joint_approval_required_flag,
        "register_required": rule.register_required,
        "effective_from": rule.effective_from.isoformat(),
        "effective_to": rule.effective_to.isoformat() if rule.effective_to else None,
        "status": rule.status, "version_number": rule.version_number,
    }


def serialize_committee(row):
    return {
        "sanction_committee_id": str(row.pk), "committee_name": row.committee_name,
        "cfo_user_id": str(row.cfo_user_id), "director_1_user_id": str(row.director_1_user_id),
        "director_2_user_id": str(row.director_2_user_id),
        "board_meeting_reference": row.board_meeting_reference,
        "effective_from": row.effective_from.isoformat(),
        "effective_to": row.effective_to.isoformat() if row.effective_to else None,
        "status": row.status, "version_number": row.version_number,
    }


def serialize_proposal(proposal, user=None):
    actions = []
    if user is not None:
        enabled = (
            proposal.status == ApprovalConfigurationProposal.STATUS_PENDING
            and proposal.made_by_user_id != user.pk
            and user.status == User.ACTIVE_STATUS
            and user.approval_authority_type in {"cfo", "company_secretary"}
        )
        reason = None if enabled else (
            "Proposal is no longer pending." if proposal.status != ApprovalConfigurationProposal.STATUS_PENDING
            else "Maker cannot approve or reject their own proposal." if proposal.made_by_user_id == user.pk
            else "Active CFO or Company Secretary approval authority is required."
        )
        for code, label in (("approvals.configuration_proposal.approve", "Approve"), ("approvals.configuration_proposal.reject", "Reject")):
            actions.append({"action_code": code, "label": label, "enabled": enabled,
                            "disabled_reason": reason, "required_permission": "",
                            "confirmation_required": True})
    return {
        "approval_configuration_proposal_id": str(proposal.pk),
        "proposal_type": proposal.proposal_type,
        "target_entity_id": str(proposal.target_entity_id) if proposal.target_entity_id else None,
        "reason": proposal.reason,
        "status": proposal.status,
        "version": proposal.version,
        "made_by_user_id": str(proposal.made_by_user_id),
        "decided_by_user_id": str(proposal.decided_by_user_id) if proposal.decided_by_user_id else None,
        "rejection_reason": proposal.rejection_reason or None,
        "available_actions": actions,
    }


def list_rules(query_params):
    return _paginated(ApprovalMatrixRule.objects.order_by("decision_type", "condition_code", "amount_min", "effective_from", "approval_matrix_rule_id"), serialize_rule, query_params)


def list_committees(query_params):
    return _paginated(SanctionCommittee.objects.order_by("-effective_from", "sanction_committee_id"), serialize_committee, query_params)


@transaction.atomic
def seed_demo_committee():
    existing = SanctionCommittee.objects.filter(
        committee_name="Demo Sanction Committee FY 2026",
        version_number="seed-2026-1",
    ).first()
    if existing is not None:
        return serialize_committee(existing)
    _lock_configuration_boundary()
    users = {
        "cfo_user": User.objects.get(email="demo.cfo@sfpcl.example"),
        "director_1_user": User.objects.get(email="demo.director1@sfpcl.example"),
        "director_2_user": User.objects.get(email="demo.director2@sfpcl.example"),
    }
    cleaned = {
        "committee_name": "Demo Sanction Committee FY 2026",
        **users,
        "board_meeting_reference": "DEMO-BOARD-2026-01",
        "effective_from": parse_date("2026-04-01"),
        "effective_to": None,
        "version_number": "seed-2026-1",
    }
    _ensure_no_committee_overlap(cleaned)
    row = SanctionCommittee.objects.create(
        **cleaned, status=SanctionCommittee.STATUS_ACTIVE
    )
    return serialize_committee(row)


@transaction.atomic
def create_rule(user, request, payload):
    reason, configuration_payload = _proposal_payload(payload)
    _validate_rule(configuration_payload)
    proposal = ApprovalConfigurationProposal.objects.create(
        proposal_type=ApprovalConfigurationProposal.TYPE_RULE_CREATE,
        payload_json=configuration_payload,
        reason=reason,
        made_by_user=user,
        request_id=request.headers.get("X-Request-ID", ""),
        request_ip=request_ip(request),
        request_user_agent=request_user_agent(request),
    )
    return serialize_proposal(proposal, user)


@transaction.atomic
def supersede_rule(user, request, rule_id, payload):
    old = ApprovalMatrixRule.objects.get(pk=rule_id)
    if old.status != ApprovalMatrixRule.STATUS_ACTIVE:
        raise ConfigurationConflict("Only an active rule can be superseded.")
    reason, configuration_payload = _proposal_payload(payload)
    cleaned = _validate_rule(configuration_payload)
    if cleaned["effective_from"] <= old.effective_from:
        raise ValidationError({"effective_from": "A replacement must start after the existing rule."})
    proposal = ApprovalConfigurationProposal.objects.create(
        proposal_type=ApprovalConfigurationProposal.TYPE_RULE_SUPERSEDE,
        target_entity_id=old.pk, payload_json=configuration_payload, reason=reason,
        made_by_user=user, request_id=request.headers.get("X-Request-ID", ""),
        request_ip=request_ip(request), request_user_agent=request_user_agent(request),
    )
    return serialize_proposal(proposal, user)


@transaction.atomic
def create_committee(user, request, payload):
    reason, configuration_payload = _proposal_payload(payload)
    _validate_committee(configuration_payload)
    proposal = ApprovalConfigurationProposal.objects.create(
        proposal_type=ApprovalConfigurationProposal.TYPE_COMMITTEE_CREATE,
        payload_json=configuration_payload, reason=reason, made_by_user=user,
        request_id=request.headers.get("X-Request-ID", ""), request_ip=request_ip(request),
        request_user_agent=request_user_agent(request),
    )
    return serialize_proposal(proposal, user)


@transaction.atomic
def supersede_committee(user, request, committee_id, payload):
    old = SanctionCommittee.objects.get(pk=committee_id)
    if old.status != SanctionCommittee.STATUS_ACTIVE:
        raise ConfigurationConflict("Only an active committee can be superseded.")
    reason, configuration_payload = _proposal_payload(payload)
    cleaned = _validate_committee(configuration_payload)
    if cleaned["effective_from"] <= old.effective_from:
        raise ValidationError({"effective_from": "A replacement must start after the existing committee."})
    proposal = ApprovalConfigurationProposal.objects.create(
        proposal_type=ApprovalConfigurationProposal.TYPE_COMMITTEE_SUPERSEDE,
        target_entity_id=old.pk, payload_json=configuration_payload, reason=reason,
        made_by_user=user, request_id=request.headers.get("X-Request-ID", ""),
        request_ip=request_ip(request), request_user_agent=request_user_agent(request),
    )
    return serialize_proposal(proposal, user)


def get_proposal(proposal_id, user):
    return serialize_proposal(ApprovalConfigurationProposal.objects.get(pk=proposal_id), user)


@transaction.atomic
def decide_proposal(proposal_id, user, request, payload, decision):
    proposal = ApprovalConfigurationProposal.objects.select_for_update().get(pk=proposal_id)
    try:
        expected_version = int(payload.get("version"))
    except (TypeError, ValueError) as exc:
        raise ValidationError({"version": "A positive integer version is required."}) from exc
    if expected_version != proposal.version:
        raise ConfigurationConflict("Proposal version is stale.", "STALE_VERSION")
    if proposal.status != ApprovalConfigurationProposal.STATUS_PENDING:
        raise ConfigurationConflict("Proposal has already been decided.", "TRANSITION_CONFLICT")
    _require_business_approver(proposal, user)
    rejection_reason = payload.get("reason")
    allowed = {"version", "reason"} if decision == "reject" else {"version"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValidationError({key: "Unknown field." for key in unknown})
    if decision == "reject" and (not isinstance(rejection_reason, str) or not rejection_reason.strip()):
        raise ValidationError({"reason": "This field is required."})
    if decision == "approve":
        _activate_proposal(proposal, user, request)
        proposal.status = ApprovalConfigurationProposal.STATUS_APPROVED
    else:
        proposal.status = ApprovalConfigurationProposal.STATUS_REJECTED
        proposal.rejection_reason = rejection_reason.strip()
    proposal.decided_by_user = user
    proposal.decided_at = timezone.now()
    proposal.version += 1
    proposal.save(update_fields=["status", "rejection_reason", "decided_by_user", "decided_at", "version"])
    return serialize_proposal(proposal, user)


def _require_business_approver(proposal, user):
    if proposal.made_by_user_id == user.pk:
        raise ConfigurationConflict("Maker cannot decide their own proposal.", "MAKER_CHECKER_VIOLATION")
    if user.status != User.ACTIVE_STATUS or user.approval_authority_type not in {"cfo", "company_secretary"}:
        raise ConfigurationConflict("Active CFO or Company Secretary approval authority is required.", "APPROVER_AUTHORITY_REQUIRED")


def _activate_proposal(proposal, approver, request):
    _lock_configuration_boundary()
    kind = proposal.proposal_type
    if kind.startswith("rule_"):
        cleaned = _validate_rule(proposal.payload_json)
        old = None
        if kind == ApprovalConfigurationProposal.TYPE_RULE_SUPERSEDE:
            old = ApprovalMatrixRule.objects.select_for_update().get(pk=proposal.target_entity_id)
            if old.status != ApprovalMatrixRule.STATUS_ACTIVE:
                raise ConfigurationConflict("Target rule is no longer active.", "PROPOSAL_STALE")
            if cleaned["effective_from"] <= old.effective_from:
                raise ConfigurationConflict("Replacement effective date is stale.", "PROPOSAL_STALE")
        _lock_rule_scope(cleaned["decision_type"], cleaned["condition_code"])
        _ensure_no_rule_overlap(cleaned, exclude_id=old.pk if old else None)
        before = serialize_rule(old) if old else None
        if old:
            old.status = ApprovalMatrixRule.STATUS_SUPERSEDED
            old.effective_to = cleaned["effective_from"] - timedelta(days=1)
            old.save(update_fields=["status", "effective_to"])
        row = ApprovalMatrixRule.objects.create(**cleaned, status=ApprovalMatrixRule.STATUS_ACTIVE)
        entity_type, after = "approval_matrix_rule", serialize_rule(row)
    else:
        cleaned = _validate_committee(proposal.payload_json)
        list(SanctionCommittee.objects.select_for_update().filter(status__in=("active", "superseded")))
        old = None
        if kind == ApprovalConfigurationProposal.TYPE_COMMITTEE_SUPERSEDE:
            old = SanctionCommittee.objects.select_for_update().get(pk=proposal.target_entity_id)
            if old.status != SanctionCommittee.STATUS_ACTIVE:
                raise ConfigurationConflict("Target committee is no longer active.", "PROPOSAL_STALE")
        _ensure_no_committee_overlap(cleaned, exclude_id=old.pk if old else None)
        before = serialize_committee(old) if old else None
        if old:
            old.status = SanctionCommittee.STATUS_SUPERSEDED
            old.effective_to = cleaned["effective_from"] - timedelta(days=1)
            old.save(update_fields=["status", "effective_to"])
        row = SanctionCommittee.objects.create(**cleaned, status=SanctionCommittee.STATUS_ACTIVE)
        entity_type, after = "sanction_committee", serialize_committee(row)
    VersionHistory.objects.create(
        versioned_entity_type=entity_type, versioned_entity_id=row.pk,
        version_number=row.version_number, change_summary=proposal.reason,
        author_user=proposal.made_by_user, approver_user=approver,
        effective_from=row.effective_from, effective_to=row.effective_to,
    )
    AuditLog.objects.create(
        actor_user=approver, action="config.changed", entity_type=entity_type, entity_id=row.pk,
        old_value_json=before,
        new_value_json={"configuration": after, "reason": proposal.reason,
                        "proposal_id": str(proposal.pk), "author_user_id": str(proposal.made_by_user_id),
                        "approver_user_id": str(approver.pk), "request_id": proposal.request_id},
        ip_address=request_ip(request), user_agent=request_user_agent(request),
    )


def _validate_rule(payload):
    required = {"decision_type", "required_approver_roles", "required_director_count",
                "joint_approval_required_flag", "effective_from", "version_number"}
    allowed = required | {"amount_min", "amount_max", "condition_code", "register_required", "effective_to"}
    errors = _unknown_missing(payload, allowed, required)
    start = _date("effective_from", payload.get("effective_from"), errors)
    end = _date("effective_to", payload.get("effective_to"), errors, optional=True)
    low = _money("amount_min", payload.get("amount_min"), errors)
    high = _money("amount_max", payload.get("amount_max"), errors)
    if low is not None and high is not None and low > high:
        errors["amount_max"] = "Must be greater than or equal to amount_min."
    if start and end and end < start:
        errors["effective_to"] = "Must be on or after effective_from."
    roles = payload.get("required_approver_roles")
    if not isinstance(roles, list) or not roles or any(not isinstance(x, str) or not x.strip() for x in roles):
        errors["required_approver_roles"] = "Must be a non-empty list of role codes."
    try:
        director_count = int(payload.get("required_director_count"))
        if director_count < 0: raise ValueError
    except (TypeError, ValueError):
        director_count = 0; errors["required_director_count"] = "Must be a non-negative integer."
    if not isinstance(payload.get("joint_approval_required_flag"), bool):
        errors["joint_approval_required_flag"] = "Must be a boolean."
    for field in ("decision_type", "version_number"):
        if not isinstance(payload.get(field), str) or not payload.get(field, "").strip(): errors[field] = "This field is required."
    if errors: raise ValidationError(errors)
    return {"decision_type": payload["decision_type"].strip(), "amount_min": low, "amount_max": high,
            "condition_code": _nullable_string(payload.get("condition_code")),
            "required_approver_roles_json": [x.strip() for x in roles],
            "required_director_count": director_count,
            "joint_approval_required_flag": payload["joint_approval_required_flag"],
            "register_required": _nullable_string(payload.get("register_required")),
            "effective_from": start, "effective_to": end, "version_number": payload["version_number"].strip()}


def _validate_committee(payload):
    required = {"committee_name", "cfo_user_id", "director_1_user_id", "director_2_user_id",
                "board_meeting_reference", "effective_from", "version_number"}
    allowed = required | {"effective_to"}; errors = _unknown_missing(payload, allowed, required)
    start = _date("effective_from", payload.get("effective_from"), errors)
    end = _date("effective_to", payload.get("effective_to"), errors, optional=True)
    if start and end and end < start: errors["effective_to"] = "Must be on or after effective_from."
    users = {}
    for field in ("cfo_user_id", "director_1_user_id", "director_2_user_id"):
        try: users[field[:-3]] = User.objects.get(pk=uuid.UUID(str(payload.get(field))))
        except (ValueError, TypeError, User.DoesNotExist): errors[field] = "Must identify an existing user."
    if len({getattr(user, "pk", None) for user in users.values()}) != 3: errors["director_1_user_id"] = "Committee members must be distinct."
    expected = {"cfo_user": "cfo", "director_1_user": "director", "director_2_user": "director"}
    for field, authority in expected.items():
        user = users.get(field)
        if user is not None and (user.status != User.ACTIVE_STATUS or user.approval_authority_type != authority):
            errors[f"{field}_id"] = f"Must identify an active user with {authority} approval authority."
    for field in ("committee_name", "board_meeting_reference", "version_number"):
        if not isinstance(payload.get(field), str) or not payload.get(field, "").strip(): errors[field] = "This field is required."
    if errors: raise ValidationError(errors)
    return {"committee_name": payload["committee_name"].strip(), **users,
            "board_meeting_reference": payload["board_meeting_reference"].strip(),
            "effective_from": start, "effective_to": end, "version_number": payload["version_number"].strip()}


def _ensure_no_rule_overlap(cleaned, exclude_id=None):
    qs = ApprovalMatrixRule.objects.filter(
        decision_type=cleaned["decision_type"],
        condition_code=cleaned["condition_code"],
        status__in=(ApprovalMatrixRule.STATUS_ACTIVE, ApprovalMatrixRule.STATUS_SUPERSEDED),
    )
    if exclude_id: qs = qs.exclude(pk=exclude_id)
    qs = _date_overlap(qs, cleaned["effective_from"], cleaned["effective_to"])
    for row in qs:
        if _ranges_overlap(cleaned["amount_min"], cleaned["amount_max"], row.amount_min, row.amount_max):
            raise ConfigurationConflict("Approval rule amount and effective ranges overlap retained history.")


def _ensure_no_committee_overlap(cleaned, exclude_id=None):
    qs = SanctionCommittee.objects.filter(
        status__in=(SanctionCommittee.STATUS_ACTIVE, SanctionCommittee.STATUS_SUPERSEDED)
    )
    if exclude_id: qs = qs.exclude(pk=exclude_id)
    if _date_overlap(qs, cleaned["effective_from"], cleaned["effective_to"]).exists():
        raise ConfigurationConflict("Committee effective range overlaps retained history.")


def _lock_rule_scope(decision_type, condition_code):
    list(ApprovalMatrixRule.objects.select_for_update().filter(decision_type=decision_type, condition_code=condition_code))


def _lock_configuration_boundary():
    ApprovalConfigurationLock.objects.select_for_update().get(lock_name="approval_matrix")


def _date_overlap(qs, start, end):
    qs = qs.filter(Q(effective_to__isnull=True) | Q(effective_to__gte=start))
    return qs if end is None else qs.filter(effective_from__lte=end)


def _ranges_overlap(a1, a2, b1, b2):
    return (a2 is None or b1 is None or a2 >= b1) and (b2 is None or a1 is None or b2 >= a1)


def _version_and_audit(user, request, entity_type, entity_id, version, start, end, action, old, new):
    VersionHistory.objects.create(versioned_entity_type=entity_type, versioned_entity_id=entity_id,
                                  version_number=version, change_summary=action, author_user=user,
                                  approver_user=user, effective_from=start, effective_to=end)
    AuditLog.objects.create(actor_user=user, action=action, entity_type=entity_type, entity_id=entity_id,
                            old_value_json=old, new_value_json=new, ip_address=request_ip(request),
                            user_agent=request_user_agent(request))


def _unknown_missing(payload, allowed, required):
    errors = {key: "Unknown field." for key in set(payload) - allowed}
    errors.update({key: "This field is required." for key in required if payload.get(key) in (None, "")})
    return errors


def _proposal_payload(payload):
    reason = payload.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ValidationError({"reason": "This field is required."})
    return reason.strip(), {key: value for key, value in payload.items() if key != "reason"}


def _date(field, value, errors, optional=False):
    if value in (None, "") and optional: return None
    parsed = parse_date(str(value)) if value is not None else None
    if parsed is None: errors[field] = "Must be a valid ISO date."
    return parsed


def _money(field, value, errors):
    if value in (None, ""): return None
    try: parsed = Decimal(str(value))
    except (InvalidOperation, ValueError): errors[field] = "Must be a finite decimal."; return None
    if not parsed.is_finite() or parsed < 0:
        errors[field] = "Must be a finite non-negative decimal."
        return None
    return parsed


def _nullable_string(value):
    return str(value).strip() or None if value is not None else None


def _decimal(value):
    return f"{value:.2f}" if value is not None else None


def _paginated(queryset, serializer, query_params):
    unknown = set(query_params.keys()) - {"page", "page_size"}
    if unknown:
        raise ValidationError({key: "Unknown query parameter." for key in sorted(unknown)})
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(_positive_int("page_size", query_params.get("page_size"), 20), 100)
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return [serializer(row) for row in queryset[offset:offset + page_size]], {
        "page": page, "page_size": page_size, "total_count": total_count,
        "total_pages": total_pages, "has_next": page < total_pages, "has_previous": page > 1,
    }


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed < 1:
        raise ValidationError({field: "Must be a positive integer."})
    return parsed
