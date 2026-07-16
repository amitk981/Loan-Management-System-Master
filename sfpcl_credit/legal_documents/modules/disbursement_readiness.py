from dataclasses import dataclass

from sfpcl_credit.legal_documents.models import (
    ChecklistAction,
    ChecklistItem,
    DocumentChecklist,
)
from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.legal_documents.modules import signatures
from sfpcl_credit.legal_documents.selectors import (
    current_loan_term_document_for_update,
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


def resolve_legal_readiness(*, application_id, terminal_security_evidence=None):
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
    items = list(ChecklistItem.objects.select_for_update().filter(
        document_checklist=checklist
    )) if checklist else []
    required_ids = {
        row.pk for row in items if row.required_flag and row.applicable_flag
    }
    completed_ids = (
        checklist_actions.borrower_safe_completed_item_ids(
            checklist, terminal_security_evidence=terminal_security_evidence
        )
        if checklist else set()
    )
    item_truth = bool(items) and completed_ids == required_ids
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
    signature_resolved = signatures.all_current_signatures_resolved(
        application_id=application_id
    )
    approvals = checklist_actions.approval_readiness(checklist)
    return LegalReadinessFacts(
        documentation_complete=terminal and item_truth,
        company_secretary_approval=approvals[
            ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL
        ],
        credit_manager_approval=approvals[
            ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL
        ],
        sanction_committee_approval=approvals[
            ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL
        ],
        term_sheet_complete=term_sheet is not None,
        loan_agreement_complete=loan_agreement is not None,
        signature_mismatch_resolved=signature_resolved,
    )


__all__ = ["LegalReadinessFacts", "resolve_legal_readiness"]
