"""Post-sanction legal checklist applicability and read boundary."""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.applications.modules.application_authority import (
    evaluate_application_object_access,
)
from sfpcl_credit.approvals.modules import document_checklist_facts
from sfpcl_credit.approvals.modules.read_scope import evaluate_approval_case_read_scope
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import ChecklistItem, DocumentChecklist
from sfpcl_credit.members.models import CancelledCheque
from sfpcl_credit.workflows.events import record_workflow_event


READ_PERMISSION = "documents.checklist.read"
CREATED_ACTION = "document_checklist.created"
CHANGED_ACTION = "document_checklist.applicability_changed"


class ChecklistAccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code
        super().__init__(error_code)


class ChecklistNotFound(Exception):
    pass


class InvalidChecklistState(Exception):
    pass


@dataclass(frozen=True)
class ItemSpec:
    code: str
    label: str
    order: int
    applicable: bool
    source: str
    blocker: str | None = None


_BASE_ITEMS = (
    ("witness_pan_aadhaar", "Witness PAN and Aadhaar"),
    ("cancelled_cheque", "Cancelled Cheque"),
    ("blank_dated_cheque", "Blank-Dated Cheque"),
    ("poa", "Power of Attorney"),
)
_DOCUMENT_TYPE_BY_ITEM = {
    "cancelled_cheque": "cancelled_cheque",
    "blank_dated_cheque": "blank_dated_cheque",
    "poa": "power_of_attorney",
    "tri_party_agreement": "tri_party_agreement",
    "sh4": "sh4",
    "cdsl_pledge": "cdsl_pledge",
    "term_sheet": "term_sheet",
    "loan_agreement": "loan_agreement",
    "bank_verification_letter": "bank_verification_letter",
    "final_checklist": "document_checklist",
}


@transaction.atomic
def refresh_for_approved_sanction(*, actor, application_id, source_reason):
    application = (
        LoanApplication.objects.select_for_update(of=("self",))
        .filter(pk=application_id)
        .first()
    )
    if application is None:
        raise ChecklistNotFound
    facts = document_checklist_facts.resolve_approved_facts(
        application_id=application.pk
    )
    if (
        application.application_status
        != LoanApplication.STATUS_APPROVED_BY_SANCTION
        or facts is None
    ):
        raise InvalidChecklistState(
            "Checklist creation requires the latest coherent approved sanction decision."
        )
    specs = _applicability_specs(application, facts)
    document_ids = _generated_document_ids(application.pk)
    checklist = (
        DocumentChecklist.objects.select_for_update()
        .filter(loan_application=application)
        .first()
    )
    created = checklist is None
    if created:
        checklist = DocumentChecklist.objects.create(loan_application=application)
    old_snapshot = _item_snapshot(checklist)
    changed = _synchronise_items(checklist, specs, document_ids)
    new_snapshot = _item_snapshot(checklist)
    if created:
        _record_creation(actor, checklist, facts, new_snapshot, source_reason)
    elif changed:
        checklist.updated_at = timezone.now()
        checklist.save(update_fields=["updated_at"])
        _record_change(
            actor, checklist, facts, old_snapshot, new_snapshot, source_reason
        )
    return checklist


def read_for_application(*, actor, application_id):
    permissions = auth_service.effective_permission_codes(actor)
    if not actor.can_authenticate() or READ_PERMISSION not in permissions:
        raise ChecklistAccessDenied("FORBIDDEN")
    checklist = (
        DocumentChecklist.objects.select_related("loan_application")
        .prefetch_related("items")
        .filter(loan_application_id=application_id)
        .first()
    )
    if checklist is None:
        raise ChecklistNotFound
    case = (
        checklist.loan_application.sanction_approval_cases.prefetch_related("actions")
        .order_by("-cycle_number", "-submitted_at")
        .first()
    )
    if case is None or not _can_read(
        actor=actor,
        application=checklist.loan_application,
        case=case,
        permissions=permissions,
    ):
        raise ChecklistAccessDenied("OBJECT_ACCESS_DENIED")
    return serialize(checklist)


def serialize(checklist):
    return {
        "document_checklist_id": str(checklist.pk),
        "loan_application_id": str(checklist.loan_application_id),
        "checklist_status": checklist.checklist_status,
        "items": [
            {
                "checklist_item_id": str(item.pk),
                "item_code": item.item_code,
                "item_label": item.item_label,
                "required_flag": item.required_flag,
                "applicable_flag": item.applicable_flag,
                "completion_status": item.completion_status,
                "applicability_source": item.applicability_source,
                "applicability_blocker": item.applicability_blocker,
                "loan_document_id": (
                    str(item.loan_document_id) if item.loan_document_id else None
                ),
            }
            for item in checklist.items.all()
        ],
        "signature_status": {
            "company_secretary": (
                "signed" if checklist.company_secretary_signature_id else "pending"
            ),
            "credit_manager": (
                "signed" if checklist.credit_manager_signature_id else "pending"
            ),
            "sanction_committee": (
                "signed" if checklist.sanction_committee_signature_id else "pending"
            ),
            "senior_manager_finance": (
                "signed"
                if checklist.senior_manager_finance_signature_id
                else "not_applicable_until_disbursement"
            ),
        },
    }


def _can_read(*, actor, application, case, permissions):
    roles = set(actor.role_codes())
    if roles & {"compliance_team_member", "company_secretary"}:
        return application.application_status == LoanApplication.STATUS_APPROVED_BY_SANCTION
    scope = evaluate_approval_case_read_scope(
        actor=actor,
        case=case,
        actor_permissions=permissions,
    )
    if scope.allowed:
        return True
    if "credit_manager" in roles:
        return evaluate_application_object_access(
            application=application,
            actor=actor,
            required_permission=READ_PERMISSION,
            actor_permissions=permissions,
        ).allowed
    return False


def _applicability_specs(application, facts):
    specs = [
        ItemSpec(code, label, index, True, "source_always_required")
        for index, (code, label) in enumerate(_BASE_ITEMS, start=1)
    ]
    subsidiary = facts.subsidiary_route is True
    specs.append(
        ItemSpec(
            "tri_party_agreement",
            "Declaration / Tri-party Agreement",
            5,
            subsidiary,
            (
                "frozen_subsidiary_repayment_route"
                if facts.subsidiary_route is not None
                else "subsidiary_route_source_missing"
            ),
            None if facts.subsidiary_route is not None else "subsidiary_route_source_missing",
        )
    )
    if facts.holding_mode == "physical":
        sh4, cdsl, blocker, source = True, False, None, "frozen_physical_shareholding"
    elif facts.holding_mode == "demat":
        sh4, cdsl, blocker, source = False, True, None, "frozen_demat_shareholding"
    elif facts.holding_mode == "mixed":
        sh4, cdsl, blocker, source = False, False, "shareholding_mode_conflicting", "frozen_shareholding_mode_conflict"
    else:
        sh4, cdsl, blocker, source = False, False, "shareholding_mode_missing", "frozen_shareholding_mode_missing"
    specs.extend(
        (
            ItemSpec("sh4", "Share Transfer Form SH-4", 6, sh4, source, blocker),
            ItemSpec("cdsl_pledge", "CDSL Pledge Evidence", 7, cdsl, source, blocker),
        )
    )
    specs.extend(
        (
            ItemSpec("term_sheet", "Term Sheet", 8, True, "source_always_required"),
            ItemSpec("loan_agreement", "Loan Agreement", 9, True, "source_always_required"),
        )
    )
    mismatch, mismatch_source, mismatch_blocker = _signature_mismatch(application)
    specs.append(
        ItemSpec(
            "bank_verification_letter",
            "Bank Verification Letter",
            10,
            mismatch,
            mismatch_source,
            mismatch_blocker,
        )
    )
    specs.append(
        ItemSpec(
            "final_checklist",
            "Final Document Checklist",
            11,
            True,
            "source_always_required",
        )
    )
    return specs


def _signature_mismatch(application):
    flags = list(
        CancelledCheque.objects.filter(
            loan_application_id=application.pk,
            member_id=application.member_id,
        ).values_list("signature_mismatch_flag", flat=True)
    )
    distinct = set(flags)
    if distinct == {True}:
        return True, "persisted_signature_mismatch", None
    if distinct == {False}:
        return False, "persisted_signature_match", None
    if distinct == {False, True}:
        return False, "persisted_signature_mismatch_conflict", "signature_mismatch_conflicting"
    return False, "signature_mismatch_source_missing", "signature_mismatch_source_missing"


def _generated_document_ids(application_id):
    by_type = selectors.latest_generated_metadata_by_type(
        application_id=application_id,
        document_types=set(_DOCUMENT_TYPE_BY_ITEM.values()),
    )
    return {
        item_code: by_type.get(document_type)
        for item_code, document_type in _DOCUMENT_TYPE_BY_ITEM.items()
    }


def _synchronise_items(checklist, specs, document_ids):
    existing = {
        item.item_code: item
        for item in checklist.items.select_for_update().order_by("display_order")
    }
    changed = False
    for spec in specs:
        values = {
            "item_label": spec.label,
            "display_order": spec.order,
            "required_flag": spec.applicable,
            "applicable_flag": spec.applicable,
            "completion_status": (
                ChecklistItem.STATUS_PENDING
                if spec.applicable
                else ChecklistItem.STATUS_NOT_APPLICABLE
            ),
            "applicability_source": spec.source,
            "applicability_blocker": spec.blocker,
            "loan_document_id": document_ids.get(spec.code),
        }
        item = existing.get(spec.code)
        if item is None:
            ChecklistItem.objects.create(
                document_checklist=checklist,
                item_code=spec.code,
                **values,
            )
            changed = True
            continue
        changed_fields = [
            field for field, value in values.items() if getattr(item, field) != value
        ]
        if changed_fields:
            for field, value in values.items():
                setattr(item, field, value)
            item.save(update_fields=changed_fields)
            changed = True
    return changed


def _item_snapshot(checklist):
    return {
        item.item_code: {
            "required_flag": item.required_flag,
            "applicable_flag": item.applicable_flag,
            "completion_status": item.completion_status,
            "applicability_source": item.applicability_source,
            "applicability_blocker": item.applicability_blocker,
            "loan_document_id": (
                str(item.loan_document_id) if item.loan_document_id else None
            ),
        }
        for item in checklist.items.order_by("display_order")
    }


def _record_creation(actor, checklist, facts, snapshot, source_reason):
    evidence = {
        "loan_application_id": str(checklist.loan_application_id),
        "approval_case_id": str(facts.approval_case_id),
        "sanction_decision_id": str(facts.sanction_decision_id),
        "source_reason": source_reason,
        "items": snapshot,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=CREATED_ACTION,
        entity_type="document_checklist",
        entity_id=checklist.pk,
        old_value_json={},
        new_value_json=evidence,
    )
    record_workflow_event(
        actor=actor,
        workflow_name="documentation_checklist",
        entity_type="document_checklist",
        entity_id=checklist.pk,
        from_state=None,
        to_state=checklist.checklist_status,
        trigger_reason="Created automatically from approved sanction facts.",
        action_code=CREATED_ACTION,
        metadata=evidence,
    )


def _record_change(actor, checklist, facts, old_snapshot, new_snapshot, source_reason):
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=CHANGED_ACTION,
        entity_type="document_checklist",
        entity_id=checklist.pk,
        old_value_json={"items": old_snapshot},
        new_value_json={
            "items": new_snapshot,
            "source_reason": source_reason,
            "approval_case_id": str(facts.approval_case_id),
            "sanction_decision_id": str(facts.sanction_decision_id),
        },
    )
    record_workflow_event(
        actor=actor,
        workflow_name="documentation_checklist",
        entity_type="document_checklist",
        entity_id=checklist.pk,
        from_state=checklist.checklist_status,
        to_state=checklist.checklist_status,
        trigger_reason=f"Applicability refreshed: {source_reason}.",
        action_code=CHANGED_ACTION,
    )
