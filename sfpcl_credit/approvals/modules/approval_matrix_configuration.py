import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.approvals.models import ApprovalConfigurationLock, ApprovalMatrixRule, SanctionCommittee
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service


READ_PERMISSION = "approvals.matrix.read"
MANAGE_PERMISSION = "approvals.matrix.manage"


class ConfigurationConflict(Exception):
    pass


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


def list_rules():
    return [serialize_rule(row) for row in ApprovalMatrixRule.objects.all()]


def list_committees():
    return [serialize_committee(row) for row in SanctionCommittee.objects.all()]


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
    cleaned = _validate_rule(payload)
    _lock_configuration_boundary()
    _lock_rule_scope(cleaned["decision_type"], cleaned["condition_code"])
    _ensure_no_rule_overlap(cleaned)
    rule = ApprovalMatrixRule.objects.create(**cleaned, status=ApprovalMatrixRule.STATUS_ACTIVE)
    _version_and_audit(user, request, "approval_matrix_rule", rule.pk, rule.version_number,
                       rule.effective_from, rule.effective_to, "approvals.matrix_rule.created", None,
                       serialize_rule(rule))
    return serialize_rule(rule)


@transaction.atomic
def supersede_rule(user, request, rule_id, payload):
    _lock_configuration_boundary()
    old = ApprovalMatrixRule.objects.select_for_update().get(pk=rule_id)
    if old.status != ApprovalMatrixRule.STATUS_ACTIVE:
        raise ConfigurationConflict("Only an active rule can be superseded.")
    cleaned = _validate_rule(payload)
    if cleaned["effective_from"] <= old.effective_from:
        raise ValidationError({"effective_from": "A replacement must start after the existing rule."})
    _lock_rule_scope(cleaned["decision_type"], cleaned["condition_code"])
    _ensure_no_rule_overlap(cleaned, exclude_id=old.pk)
    before = serialize_rule(old)
    old.status = ApprovalMatrixRule.STATUS_SUPERSEDED
    old.effective_to = cleaned["effective_from"] - timedelta(days=1)
    old.save(update_fields=["status", "effective_to"])
    replacement = ApprovalMatrixRule.objects.create(**cleaned, status=ApprovalMatrixRule.STATUS_ACTIVE)
    _version_and_audit(user, request, "approval_matrix_rule", replacement.pk,
                       replacement.version_number, replacement.effective_from, replacement.effective_to,
                       "approvals.matrix_rule.superseded", before, serialize_rule(replacement))
    return serialize_rule(replacement)


@transaction.atomic
def create_committee(user, request, payload):
    cleaned = _validate_committee(payload)
    _lock_configuration_boundary()
    list(SanctionCommittee.objects.select_for_update().filter(status="active"))
    _ensure_no_committee_overlap(cleaned)
    row = SanctionCommittee.objects.create(**cleaned, status=SanctionCommittee.STATUS_ACTIVE)
    _version_and_audit(user, request, "sanction_committee", row.pk, row.version_number,
                       row.effective_from, row.effective_to, "approvals.sanction_committee.created",
                       None, serialize_committee(row))
    return serialize_committee(row)


@transaction.atomic
def supersede_committee(user, request, committee_id, payload):
    _lock_configuration_boundary()
    old = SanctionCommittee.objects.select_for_update().get(pk=committee_id)
    if old.status != SanctionCommittee.STATUS_ACTIVE:
        raise ConfigurationConflict("Only an active committee can be superseded.")
    cleaned = _validate_committee(payload)
    if cleaned["effective_from"] <= old.effective_from:
        raise ValidationError({"effective_from": "A replacement must start after the existing committee."})
    _ensure_no_committee_overlap(cleaned, exclude_id=old.pk)
    before = serialize_committee(old)
    old.status = SanctionCommittee.STATUS_SUPERSEDED
    old.effective_to = cleaned["effective_from"] - timedelta(days=1)
    old.save(update_fields=["status", "effective_to"])
    row = SanctionCommittee.objects.create(**cleaned, status=SanctionCommittee.STATUS_ACTIVE)
    _version_and_audit(user, request, "sanction_committee", row.pk, row.version_number,
                       row.effective_from, row.effective_to, "approvals.sanction_committee.superseded",
                       before, serialize_committee(row))
    return serialize_committee(row)


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
    for field in ("committee_name", "board_meeting_reference", "version_number"):
        if not isinstance(payload.get(field), str) or not payload.get(field, "").strip(): errors[field] = "This field is required."
    if errors: raise ValidationError(errors)
    return {"committee_name": payload["committee_name"].strip(), **users,
            "board_meeting_reference": payload["board_meeting_reference"].strip(),
            "effective_from": start, "effective_to": end, "version_number": payload["version_number"].strip()}


def _ensure_no_rule_overlap(cleaned, exclude_id=None):
    qs = ApprovalMatrixRule.objects.filter(decision_type=cleaned["decision_type"], condition_code=cleaned["condition_code"], status="active")
    if exclude_id: qs = qs.exclude(pk=exclude_id)
    qs = _date_overlap(qs, cleaned["effective_from"], cleaned["effective_to"])
    for row in qs:
        if _ranges_overlap(cleaned["amount_min"], cleaned["amount_max"], row.amount_min, row.amount_max):
            raise ConfigurationConflict("Approval rule amount and effective ranges overlap an active rule.")


def _ensure_no_committee_overlap(cleaned, exclude_id=None):
    qs = SanctionCommittee.objects.filter(status="active")
    if exclude_id: qs = qs.exclude(pk=exclude_id)
    if _date_overlap(qs, cleaned["effective_from"], cleaned["effective_to"]).exists():
        raise ConfigurationConflict("Committee effective range overlaps an active committee.")


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
