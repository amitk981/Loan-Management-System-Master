from dataclasses import dataclass

from sfpcl_credit.legal_documents.models import (
    ChecklistAction,
    ChecklistItem,
    DocumentChecklist,
)
from sfpcl_credit.legal_documents.selectors import (
    current_loan_term_document_for_update,
    signature_facts_for_application,
)


@dataclass(frozen=True)
class LegalReadinessFacts:
    documentation_complete: bool
    company_secretary_approval: bool
    credit_manager_approval: bool
    sanction_committee_approval: bool
    term_sheet_complete: bool
    loan_agreement_complete: bool
    signature_mismatch_resolved: bool


def resolve_legal_readiness(*, application_id):
    """Project current legal/checklist facts without refreshing or completing them."""
    checklist = (
        DocumentChecklist.objects.select_for_update()
        .select_related(
            "company_secretary_signature",
            "credit_manager_signature",
            "sanction_committee_signature",
        )
        .filter(loan_application_id=application_id)
        .first()
    )
    items = list(
        ChecklistItem.objects.select_for_update()
        .filter(document_checklist=checklist)
        .values("required_flag", "applicable_flag", "completion_status")
    ) if checklist else []
    item_truth = bool(items) and all(
        (not row["required_flag"] and not row["applicable_flag"])
        or row["completion_status"] == ChecklistItem.STATUS_COMPLETE
        for row in items
    )
    terminal = bool(
        checklist
        and checklist.checklist_status == DocumentChecklist.STATUS_SANCTION_APPROVED
    )
    term_sheet = current_loan_term_document_for_update(
        application_id=application_id, document_type="term_sheet"
    )
    loan_agreement = current_loan_term_document_for_update(
        application_id=application_id, document_type="loan_agreement"
    )
    signatures = list(signature_facts_for_application(application_id=application_id))
    signature_resolved = all(
        row["signature_status"] != "mismatch" or bool(row["mismatch_resolution_type"])
        for row in signatures
        if row["verified_by_user_id"] and row["verified_at"]
    )
    def approval_matches(action, action_type):
        return bool(
            action
            and action.document_checklist_id == checklist.pk
            and action.action_type == action_type
            and action.workflow_event_id
            and action.audit_log_id
            and action.version_history_id
        )
    return LegalReadinessFacts(
        documentation_complete=terminal and item_truth,
        company_secretary_approval=approval_matches(
            checklist.company_secretary_signature if checklist else None,
            ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL,
        ),
        credit_manager_approval=approval_matches(
            checklist.credit_manager_signature if checklist else None,
            ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL,
        ),
        sanction_committee_approval=approval_matches(
            checklist.sanction_committee_signature if checklist else None,
            ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL,
        ),
        term_sheet_complete=term_sheet is not None,
        loan_agreement_complete=loan_agreement is not None,
        signature_mismatch_resolved=signature_resolved,
    )


__all__ = ["LegalReadinessFacts", "resolve_legal_readiness"]
