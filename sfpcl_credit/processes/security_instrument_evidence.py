"""Atomic coordinator for approval, legal-document, and security-instrument owners.

Lock order is application/package -> retained security instrument -> legal document/checklist.
Security modules decide security policy; this process supplies only locked canonical owner facts.
"""

from sfpcl_credit.approvals.models import ApprovalCase
from django.core.exceptions import ValidationError
from django.db import transaction
from sfpcl_credit.approvals.modules.document_checklist_facts import resolve_approved_facts
from sfpcl_credit.approvals.modules.read_scope import evaluate_approval_case_read_scope
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.documents.modules import sensitive_data_access
from sfpcl_credit.legal_documents.models import ChecklistItem, DocumentChecklist
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.security_instruments.evidence_contract import (
    UncoordinatedEvidence,
    _issue_security_evidence_access,
)
from sfpcl_credit.security_instruments.models import CDSLSharePledge
from sfpcl_credit.security_instruments.modules import (
    cdsl_share_pledge,
    power_of_attorney,
    security_package,
    sh4,
)

SensitiveAccessDenied = sensitive_data_access.SensitiveAccessDenied
SensitiveObjectNotFound = sensitive_data_access.SensitiveObjectNotFound
SensitiveRateLimited = sensitive_data_access.SensitiveRateLimited
SensitiveValueUnavailable = sensitive_data_access.SensitiveValueUnavailable


def _canonical_stage4_scope(application_id):
    facts = resolve_approved_facts(application_id=application_id)
    if facts is None:
        return False
    checklist = DocumentChecklist.objects.filter(loan_application_id=application_id).first()
    if checklist is None:
        return False
    rows = list(
        AuditLog.objects.filter(
            action="document_checklist.created",
            entity_type="document_checklist",
            entity_id=checklist.pk,
        ).order_by("created_at", "audit_log_id")[:2]
    )
    if len(rows) != 1:
        return False
    creation = rows[0].new_value_json or {}
    return (
        creation.get("approval_case_id") == str(facts.approval_case_id)
        and creation.get("sanction_decision_id") == str(facts.sanction_decision_id)
    )


def _approval_read_allowed(actor, application_id):
    case = (
        ApprovalCase.objects.filter(loan_application_id=application_id)
        .prefetch_related("actions")
        .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
        .first()
    )
    return bool(case and evaluate_approval_case_read_scope(actor=actor, case=case).allowed)


def _project_checklist_item(*, application_id, item_code, document, updates=None):
    item = (
        ChecklistItem.objects.select_for_update()
        .filter(
            document_checklist__loan_application_id=application_id,
            item_code=item_code,
            applicable_flag=True,
            required_flag=True,
        )
        .first()
    )
    if item is None:
        raise security_package.Conflict(f"The required {item_code} checklist item was not found.")
    item.loan_document = document
    update_fields = ["loan_document"]
    for field, value in (updates or {}).items():
        setattr(item, field, value)
        update_fields.append(field)
    item.save(update_fields=update_fields)


def _access():
    return _issue_security_evidence_access(
        approved_facts=resolve_approved_facts,
        approval_read_allowed=_approval_read_allowed,
        canonical_stage4_scope=_canonical_stage4_scope,
        poa_evidence=selectors.poa_evidence_for_update,
        execution_signatures=selectors.execution_signature_facts_for_document,
        sh4_evidence=selectors.sh4_evidence_for_update,
        cdsl_evidence=selectors.cdsl_pledge_evidence_for_update,
        project_checklist_item=_project_checklist_item,
        mask_sensitive=sensitive_data_access.mask_value,
    )


def _call_with_canonical_evidence(function, kwargs):
    if "evidence_access" in kwargs:
        raise UncoordinatedEvidence("Caller-supplied evidence authority is forbidden.")
    return function(evidence_access=_access(), **kwargs)


def read_package(**kwargs):
    return _call_with_canonical_evidence(security_package.read_package, kwargs)


def refresh_package(**kwargs):
    return _call_with_canonical_evidence(security_package.refresh_package, kwargs)


def read_poa(**kwargs):
    return _call_with_canonical_evidence(power_of_attorney.read_poa, kwargs)


def create_poa(**kwargs):
    return _call_with_canonical_evidence(power_of_attorney.create_poa, kwargs)


def update_poa(**kwargs):
    return _call_with_canonical_evidence(power_of_attorney.update_poa, kwargs)


def read_sh4(**kwargs):
    return _call_with_canonical_evidence(sh4.read_sh4, kwargs)


def create_sh4(**kwargs):
    return _call_with_canonical_evidence(sh4.create_sh4, kwargs)


def update_sh4(**kwargs):
    return _call_with_canonical_evidence(sh4.update_sh4, kwargs)


def read_pledge(**kwargs):
    return _call_with_canonical_evidence(cdsl_share_pledge.read_pledge, kwargs)


def create_pledge(**kwargs):
    return _call_with_canonical_evidence(cdsl_share_pledge.create_pledge, kwargs)


def update_pledge(**kwargs):
    return _call_with_canonical_evidence(cdsl_share_pledge.update_pledge, kwargs)


def reveal_bo_accounts(**kwargs):
    if "evidence_access" in kwargs:
        raise UncoordinatedEvidence("Caller-supplied evidence authority is forbidden.")
    actor = kwargs["actor"]
    pledge_id = kwargs["cdsl_share_pledge_id"]
    access = _access()

    def resolve_entity(resolving_actor):
        package_id = (
            CDSLSharePledge.objects.filter(pk=pledge_id)
            .values_list("security_package_id", flat=True)
            .first()
        )
        if package_id is None:
            return None
        try:
            security_package.resolve_package(
                resolving_actor,
                package_id,
                security_package.READ_PERMISSION,
                evidence_access=access,
            )
        except security_package.AccessDenied as exc:
            raise sensitive_data_access.SensitiveAccessDenied from exc
        pledge = (
            CDSLSharePledge.objects.select_for_update()
            .select_related("security_package")
            .filter(pk=pledge_id, security_package_id=package_id)
            .first()
        )
        if pledge is None:
            return None
        facts = cdsl_share_pledge.sensitive_entity_facts(pledge)
        return sensitive_data_access.SensitiveEntity(**facts)

    denied = None
    with transaction.atomic():
        try:
            revealed = sensitive_data_access.reveal_cdsl_bo_accounts(
                actor=actor,
                cdsl_share_pledge_id=pledge_id,
                payload=kwargs["payload"],
                metadata=sensitive_data_access.RequestMetadata(
                    request_id=kwargs["metadata"].request_id,
                    ip_address=kwargs["metadata"].ip_address,
                    user_agent=kwargs["metadata"].user_agent,
                ),
                resolve_entity=resolve_entity,
            )
        except (
            ValidationError,
            SensitiveAccessDenied,
            SensitiveRateLimited,
            SensitiveValueUnavailable,
        ) as exc:
            # The central policy has already written its denial evidence. Leave the
            # lock transaction normally so that evidence commits, then preserve the
            # same transport/domain exception for the HTTP adapter.
            denied = exc
    if denied is not None:
        raise denied
    return {
        "cdsl_share_pledge_id": str(pledge_id),
        **revealed,
    }
