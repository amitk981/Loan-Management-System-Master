"""Post-sanction legal checklist applicability and read boundary."""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.applications.modules import document_checklist_facts as application_facts
from sfpcl_credit.approvals.modules import document_checklist_facts
from sfpcl_credit.approvals.modules import document_checklist_access
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import ChecklistItem, DocumentChecklist
from sfpcl_credit.workflows.events import record_workflow_event


CREATED_ACTION = "document_checklist.created"
CHANGED_ACTION = "document_checklist.applicability_changed"
LINKED_ACTION = "document_checklist.linkage_changed"


class ChecklistAccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code
        super().__init__(error_code)


class ChecklistNotFound(Exception):
    pass


class PreSanctionChecklist(Exception):
    pass


class InvalidChecklistState(Exception):
    pass


class ChecklistApplicabilityConflict(Exception):
    pass


@dataclass(frozen=True)
class ItemSpec:
    code: str
    label: str
    order: int
    applicable: bool
    source: str
    blocker: str | None = None


@dataclass(frozen=True)
class SynchronisationResult:
    applicability_changed: bool = False
    linkage_changed: bool = False


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
def refresh_for_approved_sanction(
    *, actor, application_id, source_reason, request_meta=None
):
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
    changes = _synchronise_items(checklist, specs, document_ids)
    new_snapshot = _item_snapshot(checklist)
    if created:
        _record_creation(
            actor, checklist, facts, new_snapshot, source_reason, request_meta
        )
    elif changes.applicability_changed or changes.linkage_changed:
        checklist.updated_at = timezone.now()
        checklist.save(update_fields=["updated_at"])
        if changes.applicability_changed:
            _record_change(
                actor,
                checklist,
                facts,
                old_snapshot,
                new_snapshot,
                source_reason,
                request_meta,
            )
        if changes.linkage_changed:
            _record_linkage_change(
                actor,
                checklist,
                facts,
                old_snapshot,
                new_snapshot,
                source_reason,
                request_meta,
            )
    return checklist


def read_for_application(*, actor, application_id):
    resolution = document_checklist_access.resolve_read_access(
        actor=actor, application_id=application_id
    )
    if resolution.route == document_checklist_access.ROUTE_PRE_SANCTION:
        raise PreSanctionChecklist
    if resolution.error_code == "NOT_FOUND":
        raise ChecklistNotFound
    if resolution.error_code:
        raise ChecklistAccessDenied(resolution.error_code)
    application = resolution.application
    checklist = (
        DocumentChecklist.objects.prefetch_related("items")
        .filter(loan_application=application)
        .first()
    )
    if checklist is None:
        raise ChecklistNotFound
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
    fact = application_facts.resolve_cancelled_cheque_signature_fact(
        application_id=application.pk,
        member_id=application.member_id,
    )
    return fact.mismatch is True, fact.source, fact.blocker


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
    applicability_changed = False
    linkage_changed = False
    for spec in specs:
        applicability_values = {
            "required_flag": spec.applicable,
            "applicable_flag": spec.applicable,
            "applicability_source": spec.source,
            "applicability_blocker": spec.blocker,
        }
        item = existing.get(spec.code)
        if item is None:
            ChecklistItem.objects.create(
                document_checklist=checklist,
                item_code=spec.code,
                completion_status=(
                    ChecklistItem.STATUS_PENDING
                    if spec.applicable
                    else ChecklistItem.STATUS_NOT_APPLICABLE
                ),
                item_label=spec.label,
                display_order=spec.order,
                loan_document_id=document_ids.get(spec.code),
                **applicability_values,
            )
            applicability_changed = True
            continue
        changed_applicability_fields = [
            field
            for field, value in applicability_values.items()
            if getattr(item, field) != value
        ]
        applicability_flipped = item.applicable_flag != spec.applicable
        if (
            applicability_flipped
            and item.completion_status == ChecklistItem.STATUS_COMPLETE
        ):
            raise ChecklistApplicabilityConflict(
                f"Completed checklist item '{item.item_code}' conflicts with corrected applicability."
            )
        if changed_applicability_fields:
            for field, value in applicability_values.items():
                setattr(item, field, value)
            if applicability_flipped:
                item.completion_status = (
                    ChecklistItem.STATUS_PENDING
                    if spec.applicable
                    else ChecklistItem.STATUS_NOT_APPLICABLE
                )
                changed_applicability_fields.append("completion_status")
            item.save(update_fields=changed_applicability_fields)
            applicability_changed = True
        loan_document_id = document_ids.get(spec.code)
        if item.loan_document_id != loan_document_id:
            item.loan_document_id = loan_document_id
            item.save(update_fields=["loan_document"])
            linkage_changed = True
    return SynchronisationResult(
        applicability_changed=applicability_changed,
        linkage_changed=linkage_changed,
    )


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


def _applicability_snapshot(snapshot):
    """Project only facts owned by applicability synchronisation."""
    return {
        code: {
            key: value
            for key, value in facts.items()
            if key != "loan_document_id"
        }
        for code, facts in snapshot.items()
    }


def _linkage_snapshot(snapshot):
    """Project only the generated-document relationship owned by linkage."""
    return {
        code: {"loan_document_id": facts["loan_document_id"]}
        for code, facts in snapshot.items()
    }


def _record_creation(
    actor, checklist, facts, snapshot, source_reason, request_meta=None
):
    context = _audit_context(actor, request_meta)
    evidence = {
        "loan_application_id": str(checklist.loan_application_id),
        "approval_case_id": str(facts.approval_case_id),
        "sanction_decision_id": str(facts.sanction_decision_id),
        "source_reason": source_reason,
        "items": snapshot,
        **context,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=CREATED_ACTION,
        entity_type="document_checklist",
        entity_id=checklist.pk,
        old_value_json={},
        new_value_json=evidence,
        ip_address=(request_meta or {}).get("ip_address", ""),
        user_agent=(request_meta or {}).get("user_agent", ""),
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


def _record_change(
    actor,
    checklist,
    facts,
    old_snapshot,
    new_snapshot,
    source_reason,
    request_meta=None,
):
    old_snapshot = _applicability_snapshot(old_snapshot)
    new_snapshot = _applicability_snapshot(new_snapshot)
    context = _audit_context(actor, request_meta)
    evidence = {
        "source_reason": source_reason,
        "approval_case_id": str(facts.approval_case_id),
        "sanction_decision_id": str(facts.sanction_decision_id),
        **context,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=CHANGED_ACTION,
        entity_type="document_checklist",
        entity_id=checklist.pk,
        old_value_json={"items": old_snapshot},
        new_value_json={
            "items": new_snapshot,
            **evidence,
        },
        ip_address=(request_meta or {}).get("ip_address", ""),
        user_agent=(request_meta or {}).get("user_agent", ""),
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
        metadata=evidence,
    )


def _record_linkage_change(
    actor,
    checklist,
    facts,
    old_snapshot,
    new_snapshot,
    source_reason,
    request_meta=None,
):
    old_snapshot = _linkage_snapshot(old_snapshot)
    new_snapshot = _linkage_snapshot(new_snapshot)
    context = _audit_context(actor, request_meta)
    evidence = {
        "source_reason": source_reason,
        "approval_case_id": str(facts.approval_case_id),
        "sanction_decision_id": str(facts.sanction_decision_id),
        **context,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=LINKED_ACTION,
        entity_type="document_checklist",
        entity_id=checklist.pk,
        old_value_json={"items": old_snapshot},
        new_value_json={
            "items": new_snapshot,
            **evidence,
        },
        ip_address=(request_meta or {}).get("ip_address", ""),
        user_agent=(request_meta or {}).get("user_agent", ""),
    )
    record_workflow_event(
        actor=actor,
        workflow_name="documentation_checklist",
        entity_type="document_checklist",
        entity_id=checklist.pk,
        from_state=checklist.checklist_status,
        to_state=checklist.checklist_status,
        trigger_reason=f"Generated-document metadata linked: {source_reason}.",
        action_code=LINKED_ACTION,
        metadata=evidence,
    )


def _audit_context(actor, request_meta):
    request_meta = request_meta or {}
    return {
        "request_id": request_meta.get("request_id"),
        "actor_role_codes": actor.role_codes(),
        "actor_team_codes": actor.team_codes(),
    }
