from dataclasses import dataclass
import hashlib
import json
import re
import uuid

from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.configurations.models import (
    SourceBankAccountGovernance,
    VersionHistory,
)
from sfpcl_credit.identity.models import AuditLog, Permission, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import BankAccount


ACTIVATE_PERMISSION = "config.source_bank_account.activate"
ENTITY_TYPE = "source_bank_account_governance"
MAX_REASON_LENGTH = 500


class SourceBankGovernanceDenied(Exception):
    pass


class SourceBankGovernanceConflict(Exception):
    pass


@dataclass(frozen=True)
class SourceBankAccountDecision:
    source_bank_account_id: object
    active: bool
    bank_name: str
    governance_id: object
    version_history_id: object
    audit_log_id: object
    request_id: str
    source_facts_digest: str


def activate_source_bank_account(
    *, actor, bank_account_id, reason, request_id, request=None
) -> SourceBankAccountDecision:
    clean_reason = _clean_reason(reason)
    clean_request_id = request_id.strip() if isinstance(request_id, str) else ""
    if not clean_reason or not clean_request_id:
        raise SourceBankGovernanceDenied(
            "A reason and request identity are required for source-bank activation."
        )
    observed_current_id = (
        SourceBankAccountGovernance.objects.filter(
            status=SourceBankAccountGovernance.STATUS_ACTIVE
        )
        .values_list("pk", flat=True)
        .first()
    )
    with transaction.atomic():
        provisioner = _locked_provisioner(actor)
        bank = BankAccount.objects.select_for_update().filter(pk=bank_account_id).first()
        if not _eligible_bank(bank):
            raise SourceBankGovernanceDenied(
                "The source account is not an active verified SFPCL RBL account."
            )
        if _contains_sensitive_bank_content(clean_reason, bank):
            raise SourceBankGovernanceDenied(
                "The reason must not contain bank numbers or protected token content."
            )
        current = SourceBankAccountGovernance.objects.select_for_update().filter(
            status=SourceBankAccountGovernance.STATUS_ACTIVE
        ).first()
        if getattr(current, "pk", None) != observed_current_id:
            raise SourceBankGovernanceConflict(
                "The governed source-bank decision changed concurrently."
            )
        if current is not None and current.bank_account_id == bank.pk:
            raise SourceBankGovernanceConflict(
                "A governed source-bank account is already active."
            )
        now = timezone.now()
        facts_digest = _source_facts_digest(bank)
        reason_digest = _digest(clean_reason)
        change_context = _change_context(
            actor=provisioner,
            change_kind="replacement" if current is not None else "activation",
            reason=clean_reason,
            reason_digest=reason_digest,
            request_id=clean_request_id,
            request=request,
        )
        change_context_digest = _digest(change_context)
        row_id = uuid.uuid4()
        try:
            with transaction.atomic():
                old_evidence = None
                if current is not None:
                    old_evidence = _deactivate_for_successor(
                        current,
                        successor_id=row_id,
                        successor_context=change_context,
                        successor_context_digest=change_context_digest,
                        actor=provisioner,
                        changed_at=now,
                        request=request,
                    )
                row = SourceBankAccountGovernance(
                    source_bank_account_governance_id=row_id,
                    bank_account=bank,
                    predecessor=current,
                    source_facts_digest=facts_digest,
                    reason_digest=reason_digest,
                    reason=clean_reason,
                    change_context_json=change_context,
                    change_context_digest=change_context_digest,
                    request_id=clean_request_id,
                    activated_by_user=provisioner,
                    activated_at=now,
                )
                safe_evidence = _activation_evidence(row)
                history = VersionHistory.objects.create(
                    versioned_entity_type=ENTITY_TYPE,
                    versioned_entity_id=row.pk,
                    version_number="1",
                    change_summary=(
                        "Source-bank account activated through explicit authority."
                    ),
                    author_user=provisioner,
                    old_value_json=old_evidence,
                    new_value_json=safe_evidence,
                    effective_from=now.date(),
                    created_at=now,
                )
                audit = AuditLog.objects.create(
                    actor_user=provisioner,
                    actor_type="user",
                    action="config.changed",
                    entity_type=ENTITY_TYPE,
                    entity_id=row.pk,
                    old_value_json=old_evidence,
                    new_value_json=safe_evidence,
                    ip_address=request_ip(request) if request else "",
                    user_agent=request_user_agent(request) if request else "",
                    created_at=now,
                )
                row.version_history = history
                row.activation_audit = audit
                row.save(force_insert=True)
        except IntegrityError as exc:
            raise SourceBankGovernanceConflict(
                "A concurrent source-bank activation already won."
            ) from exc
        return _decision(row)


def resolve_source_bank_account(*, for_update=False):
    queryset = SourceBankAccountGovernance.objects.select_related(
        "bank_account",
        "version_history",
        "activation_audit",
        "predecessor",
        "deactivation_version_history",
        "deactivation_audit",
    )
    if for_update:
        queryset = queryset.select_for_update(of=("self", "bank_account"))
    rows = list(queryset.order_by("activated_at", "source_bank_account_governance_id"))
    active_rows = [
        row for row in rows if row.status == SourceBankAccountGovernance.STATUS_ACTIVE
    ]
    if len(active_rows) != 1:
        return None
    row = active_rows[0]
    by_id = {item.pk: item for item in rows}
    visited = set()
    successor = None
    cursor = row
    while cursor is not None:
        expected_history_ids = {cursor.version_history_id}
        expected_audit_ids = {cursor.activation_audit_id}
        if cursor.status == SourceBankAccountGovernance.STATUS_INACTIVE:
            expected_history_ids.add(cursor.deactivation_version_history_id)
            expected_audit_ids.add(cursor.deactivation_audit_id)
        retained_history_ids = set(
            VersionHistory.objects.filter(
                versioned_entity_type=ENTITY_TYPE,
                versioned_entity_id=cursor.pk,
            ).values_list("pk", flat=True)
        )
        retained_audit_ids = set(
            AuditLog.objects.filter(
                action="config.changed",
                entity_type=ENTITY_TYPE,
                entity_id=cursor.pk,
            ).values_list("pk", flat=True)
        )
        if (
            cursor.pk in visited
            or cursor.source_facts_digest != _source_facts_digest(cursor.bank_account)
            or retained_history_ids != expected_history_ids
            or retained_audit_ids != expected_audit_ids
            or not _activation_coherent(cursor)
        ):
            return None
        visited.add(cursor.pk)
        if successor is not None and not _deactivation_coherent(cursor, successor):
            return None
        successor = cursor
        cursor = by_id.get(cursor.predecessor_id) if cursor.predecessor_id else None
    if len(visited) != len(rows):
        return None
    bank = row.bank_account
    if not _eligible_bank(bank) or row.source_facts_digest != _source_facts_digest(bank):
        return None
    return _decision(row)


def _deactivate_for_successor(
    row,
    *,
    successor_id,
    successor_context,
    successor_context_digest,
    actor,
    changed_at,
    request,
):
    old_evidence = _activation_evidence(row)
    row.status = SourceBankAccountGovernance.STATUS_INACTIVE
    row.deactivated_at = changed_at
    new_evidence = _inactive_evidence(
        row,
        successor_id=successor_id,
        replacement_context=successor_context,
        replacement_context_digest=successor_context_digest,
    )
    history = VersionHistory.objects.create(
        versioned_entity_type=ENTITY_TYPE,
        versioned_entity_id=row.pk,
        version_number="2",
        change_summary="Source-bank account deactivated by governed replacement.",
        author_user=actor,
        old_value_json=old_evidence,
        new_value_json=new_evidence,
        effective_from=changed_at.date(),
        effective_to=changed_at.date(),
        created_at=changed_at,
    )
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="config.changed",
        entity_type=ENTITY_TYPE,
        entity_id=row.pk,
        old_value_json=old_evidence,
        new_value_json=new_evidence,
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
        created_at=changed_at,
    )
    row.deactivation_version_history = history
    row.deactivation_audit = audit
    row.save(
        update_fields=[
            "status",
            "deactivated_at",
            "deactivation_version_history",
            "deactivation_audit",
        ]
    )
    VersionHistory.objects.filter(pk=row.version_history_id).update(
        effective_to=changed_at.date()
    )
    row.version_history.effective_to = changed_at.date()
    return new_evidence


def _locked_provisioner(actor):
    user = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None), status=User.ACTIVE_STATUS)
        .first()
    )
    permission = (
        Permission.objects.select_for_update()
        .filter(permission_code=ACTIVATE_PERMISSION)
        .first()
    )
    if (
        user is None
        or not user.can_authenticate()
        or user.primary_role.status != "active"
        or permission is None
        or permission.risk_level != Permission.RISK_CRITICAL
        or ACTIVATE_PERMISSION not in auth_service.effective_permission_codes(user)
    ):
        raise SourceBankGovernanceDenied(
            "Explicit critical source-bank activation authority is required."
        )
    return user


def _eligible_bank(bank):
    return bool(
        bank
        and bank.owner_party_type == "sfpcl"
        and bank.bank_name.casefold() == "rbl bank"
        and bank.verification_status == "verified"
        and bank.status == "active"
    )


def _source_facts_digest(bank):
    return _digest(
        {
            "bank_account_id": str(bank.pk),
            "owner_party_type": bank.owner_party_type,
            "owner_party_id": str(bank.owner_party_id),
            "bank_name": bank.bank_name.casefold(),
            "ifsc": bank.ifsc.casefold(),
            "verification_status": bank.verification_status,
            "status": bank.status,
        }
    )


def _clean_reason(value):
    reason = value.strip() if isinstance(value, str) else ""
    if not reason:
        return ""
    if len(reason) > MAX_REASON_LENGTH or not reason.isprintable():
        raise SourceBankGovernanceDenied(
            "The reason must be printable and at most 500 characters."
        )
    if re.search(r"(?<!\d)\d{8,}(?!\d)", reason):
        raise SourceBankGovernanceDenied(
            "The reason must not contain bank numbers or protected token content."
        )
    lowered = reason.casefold()
    if any(marker in lowered for marker in ("enc:v", "aes-gcm", "ciphertext:")):
        raise SourceBankGovernanceDenied(
            "The reason must not contain bank numbers or protected token content."
        )
    return reason


def _contains_sensitive_bank_content(reason, bank):
    lowered = reason.casefold()
    protected_values = (
        bank.account_number_encrypted,
        bank.account_number_hash,
    )
    return any(
        isinstance(value, str)
        and len(value.strip()) >= 4
        and value.strip().casefold() in lowered
        for value in protected_values
    )


def _change_context(
    *, actor, change_kind, reason, reason_digest, request_id, request
):
    return {
        "action": "config.changed",
        "change_kind": change_kind,
        "reason": reason,
        "reason_digest": reason_digest,
        "request_id": request_id,
        "actor_user_id": str(actor.pk),
        "actor_role_codes": sorted(auth_service.effective_role_codes(actor)),
        "actor_team_codes": sorted(actor.team_codes()),
        "ip_address": request_ip(request) if request else "",
        "user_agent": request_user_agent(request) if request else "",
    }


def _activation_evidence(row):
    return {
        "governance_id": str(row.pk),
        "source_bank_account_id": str(row.bank_account_id),
        "predecessor_governance_id": (
            str(row.predecessor_id) if row.predecessor_id else None
        ),
        "source_facts_digest": row.source_facts_digest,
        "reason_digest": row.reason_digest,
        "request_id": row.request_id,
        "change_context": row.change_context_json,
        "change_context_digest": row.change_context_digest,
        "status": SourceBankAccountGovernance.STATUS_ACTIVE,
        "activated_by_user_id": str(row.activated_by_user_id),
        "activated_at": row.activated_at.isoformat().replace("+00:00", "Z"),
    }


def _inactive_evidence(
    row,
    *,
    successor_id,
    replacement_context,
    replacement_context_digest,
):
    return {
        **_activation_evidence(row),
        "status": SourceBankAccountGovernance.STATUS_INACTIVE,
        "deactivated_at": row.deactivated_at.isoformat().replace("+00:00", "Z"),
        "successor_governance_id": str(successor_id),
        "replacement_context": replacement_context,
        "replacement_context_digest": replacement_context_digest,
    }


def _activation_coherent(row):
    if row.version_history_id is None or row.activation_audit_id is None:
        return False
    expected = _activation_evidence(row)
    predecessor = row.predecessor
    expected_old = (
        _inactive_evidence(
            predecessor,
            successor_id=row.pk,
            replacement_context=row.change_context_json,
            replacement_context_digest=row.change_context_digest,
        )
        if predecessor is not None and predecessor.deactivated_at is not None
        else None
    )
    history = row.version_history
    audit = row.activation_audit
    audit_evidence = audit.new_value_json or {}
    return bool(
        history.versioned_entity_type == ENTITY_TYPE
        and _change_context_coherent(row)
        and history.versioned_entity_id == row.pk
        and history.version_number == "1"
        and history.change_summary
        == "Source-bank account activated through explicit authority."
        and history.author_user_id == row.activated_by_user_id
        and history.reviewer_user_id is None
        and history.approver_user_id is None
        and history.board_approval_reference is None
        and history.approval_reference == ""
        and history.approved_at is None
        and history.created_at == row.activated_at
        and history.effective_from == row.activated_at.date()
        and history.effective_to
        == (row.deactivated_at.date() if row.deactivated_at else None)
        and history.old_value_json == expected_old
        and history.new_value_json == expected
        and audit.action == "config.changed"
        and audit.entity_type == ENTITY_TYPE
        and audit.entity_id == row.pk
        and audit.actor_user_id == row.activated_by_user_id
        and audit.actor_type == "user"
        and audit.created_at == row.activated_at
        and audit.old_value_json == expected_old
        and audit_evidence == expected
        and audit.ip_address == row.change_context_json["ip_address"]
        and audit.user_agent == row.change_context_json["user_agent"]
    )


def _deactivation_coherent(row, successor):
    if (
        row.status != SourceBankAccountGovernance.STATUS_INACTIVE
        or row.deactivated_at is None
        or row.deactivation_version_history_id is None
        or row.deactivation_audit_id is None
        or successor.predecessor_id != row.pk
        or successor.activated_at != row.deactivated_at
    ):
        return False
    old_evidence = _activation_evidence(row)
    expected = _inactive_evidence(
        row,
        successor_id=successor.pk,
        replacement_context=successor.change_context_json,
        replacement_context_digest=successor.change_context_digest,
    )
    history = row.deactivation_version_history
    audit = row.deactivation_audit
    audit_evidence = audit.new_value_json or {}
    return bool(
        history.versioned_entity_type == ENTITY_TYPE
        and _change_context_coherent(successor)
        and history.versioned_entity_id == row.pk
        and history.version_number == "2"
        and history.change_summary
        == "Source-bank account deactivated by governed replacement."
        and history.author_user_id == successor.activated_by_user_id
        and history.reviewer_user_id is None
        and history.approver_user_id is None
        and history.board_approval_reference is None
        and history.approval_reference == ""
        and history.approved_at is None
        and history.created_at == row.deactivated_at
        and history.effective_from == row.deactivated_at.date()
        and history.effective_to == row.deactivated_at.date()
        and history.old_value_json == old_evidence
        and history.new_value_json == expected
        and audit.action == "config.changed"
        and audit.entity_type == ENTITY_TYPE
        and audit.entity_id == row.pk
        and audit.actor_user_id == successor.activated_by_user_id
        and audit.actor_type == "user"
        and audit.created_at == row.deactivated_at
        and audit.old_value_json == old_evidence
        and audit_evidence == expected
        and audit.ip_address == successor.change_context_json["ip_address"]
        and audit.user_agent == successor.change_context_json["user_agent"]
    )


def _change_context_coherent(row):
    context = row.change_context_json
    if not isinstance(context, dict):
        return False
    expected_keys = {
        "action",
        "change_kind",
        "reason",
        "reason_digest",
        "request_id",
        "actor_user_id",
        "actor_role_codes",
        "actor_team_codes",
        "ip_address",
        "user_agent",
    }
    return bool(
        set(context) == expected_keys
        and isinstance(row.reason, str)
        and row.reason
        and len(row.reason) <= MAX_REASON_LENGTH
        and row.reason.isprintable()
        and context["action"] == "config.changed"
        and context["change_kind"]
        == ("replacement" if row.predecessor_id else "activation")
        and context["reason"] == row.reason
        and context["reason_digest"] == row.reason_digest == _digest(row.reason)
        and context["request_id"] == row.request_id
        and context["actor_user_id"] == str(row.activated_by_user_id)
        and isinstance(context["actor_role_codes"], list)
        and bool(context["actor_role_codes"])
        and isinstance(context["actor_team_codes"], list)
        and isinstance(context["ip_address"], str)
        and isinstance(context["user_agent"], str)
        and row.change_context_digest == _digest(context)
    )


def _digest(value):
    encoded = value if isinstance(value, str) else json.dumps(
        value, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def _decision(row):
    return SourceBankAccountDecision(
        source_bank_account_id=row.bank_account_id,
        active=True,
        bank_name=row.bank_account.bank_name,
        governance_id=row.pk,
        version_history_id=row.version_history_id,
        audit_log_id=row.activation_audit_id,
        request_id=row.request_id,
        source_facts_digest=row.source_facts_digest,
    )


__all__ = [
    "SourceBankAccountDecision",
    "SourceBankGovernanceConflict",
    "SourceBankGovernanceDenied",
    "activate_source_bank_account",
    "resolve_source_bank_account",
]
