from dataclasses import dataclass
import hashlib
import json

from django.db import transaction
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
    clean_reason = reason.strip() if isinstance(reason, str) else ""
    clean_request_id = request_id.strip() if isinstance(request_id, str) else ""
    if not clean_reason or not clean_request_id:
        raise SourceBankGovernanceDenied(
            "A reason and request identity are required for source-bank activation."
        )
    with transaction.atomic():
        provisioner = _locked_provisioner(actor)
        bank = BankAccount.objects.select_for_update().filter(pk=bank_account_id).first()
        if not _eligible_bank(bank):
            raise SourceBankGovernanceDenied(
                "The source account is not an active verified SFPCL RBL account."
            )
        current = SourceBankAccountGovernance.objects.select_for_update().filter(
            status=SourceBankAccountGovernance.STATUS_ACTIVE
        ).first()
        if current is not None and current.bank_account_id == bank.pk:
            raise SourceBankGovernanceConflict(
                "A governed source-bank account is already active."
            )
        now = timezone.now()
        old_evidence = _safe_evidence(current) if current is not None else {}
        if current is not None:
            current.status = SourceBankAccountGovernance.STATUS_INACTIVE
            current.save(update_fields=["status"])
        facts_digest = _source_facts_digest(bank)
        reason_digest = _digest(clean_reason)
        row = SourceBankAccountGovernance.objects.create(
            bank_account=bank,
            source_facts_digest=facts_digest,
            reason_digest=reason_digest,
            request_id=clean_request_id,
            activated_by_user=provisioner,
            activated_at=now,
        )
        safe_evidence = _safe_evidence(row)
        history = VersionHistory.objects.create(
            versioned_entity_type=ENTITY_TYPE,
            versioned_entity_id=row.pk,
            version_number="1",
            change_summary="Source-bank account activated through explicit authority.",
            author_user=provisioner,
            approver_user=provisioner,
            approval_reference=clean_request_id,
            approved_at=now,
            old_value_json=None,
            new_value_json=safe_evidence,
            effective_from=now.date(),
            created_at=now,
        )
        audit_evidence = {
            **safe_evidence,
            "actor_role_codes": sorted(auth_service.effective_role_codes(provisioner)),
            "actor_team_codes": sorted(provisioner.team_codes()),
            "reason": "sha256:" + reason_digest,
        }
        audit = AuditLog.objects.create(
            actor_user=provisioner,
            actor_type="user",
            action="config.changed",
            entity_type=ENTITY_TYPE,
            entity_id=row.pk,
            old_value_json=old_evidence,
            new_value_json=audit_evidence,
            ip_address=request_ip(request) if request else "",
            user_agent=request_user_agent(request) if request else "",
        )
        row.version_history = history
        row.activation_audit = audit
        row.save(update_fields=["version_history", "activation_audit"])
        return _decision(row)


def resolve_source_bank_account(*, for_update=False):
    queryset = SourceBankAccountGovernance.objects.select_related(
        "bank_account", "version_history", "activation_audit"
    )
    if for_update:
        queryset = queryset.select_for_update(of=("self", "bank_account"))
    rows = list(
        queryset.filter(status=SourceBankAccountGovernance.STATUS_ACTIVE).order_by(
            "source_bank_account_governance_id"
        )[:2]
    )
    if len(rows) != 1:
        return None
    row = rows[0]
    bank = row.bank_account
    expected = _safe_evidence(row)
    audit_evidence = row.activation_audit.new_value_json or {}
    if (
        not _eligible_bank(bank)
        or row.version_history_id is None
        or row.activation_audit_id is None
        or row.source_facts_digest != _source_facts_digest(bank)
        or row.version_history.versioned_entity_type != ENTITY_TYPE
        or row.version_history.versioned_entity_id != row.pk
        or row.version_history.version_number != "1"
        or row.version_history.author_user_id != row.activated_by_user_id
        or row.version_history.approver_user_id != row.activated_by_user_id
        or row.version_history.approval_reference != row.request_id
        or row.version_history.approved_at != row.activated_at
        or row.version_history.old_value_json is not None
        or row.version_history.new_value_json != expected
        or row.activation_audit.action != "config.changed"
        or row.activation_audit.entity_type != ENTITY_TYPE
        or row.activation_audit.entity_id != row.pk
        or row.activation_audit.actor_user_id != row.activated_by_user_id
        or any(audit_evidence.get(key) != value for key, value in expected.items())
        or not audit_evidence.get("actor_role_codes")
        or not isinstance(audit_evidence.get("actor_team_codes"), list)
        or audit_evidence.get("reason") != "sha256:" + row.reason_digest
    ):
        return None
    return _decision(row)


def _locked_provisioner(actor):
    user = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None), status=User.ACTIVE_STATUS)
        .first()
    )
    permission = Permission.objects.filter(permission_code=ACTIVATE_PERMISSION).first()
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


def _safe_evidence(row):
    return {
        "governance_id": str(row.pk),
        "source_bank_account_id": str(row.bank_account_id),
        "source_facts_digest": row.source_facts_digest,
        "reason_digest": row.reason_digest,
        "request_id": row.request_id,
        "status": row.status,
        "activated_by_user_id": str(row.activated_by_user_id),
        "activated_at": row.activated_at.isoformat().replace("+00:00", "Z"),
    }


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
