"""Public coordinator for legal-checklist actions that consume security-owned facts."""

from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.processes import security_instrument_evidence


_terminal_security_evidence = security_instrument_evidence.terminal_checklist_evidence


def complete_item(**kwargs):
    return checklist_actions.complete_item(
        terminal_security_evidence=_terminal_security_evidence, **kwargs
    )


def item_completion_decision(**kwargs):
    return checklist_actions.item_completion_decision(
        terminal_security_evidence=_terminal_security_evidence, **kwargs
    )


def borrower_safe_completed_item_ids(checklist):
    return checklist_actions.borrower_safe_completed_item_ids(
        checklist, terminal_security_evidence=_terminal_security_evidence
    )


def approve_company_secretary(**kwargs):
    return checklist_actions.approve_company_secretary(
        terminal_security_evidence=_terminal_security_evidence, **kwargs
    )


def approve_credit_manager(**kwargs):
    return checklist_actions.approve_credit_manager(
        terminal_security_evidence=_terminal_security_evidence, **kwargs
    )


def approve_sanction_committee(**kwargs):
    return checklist_actions.approve_sanction_committee(
        terminal_security_evidence=_terminal_security_evidence, **kwargs
    )


def sign_disbursement_complete(**kwargs):
    return checklist_actions.sign_disbursement_complete(**kwargs)
