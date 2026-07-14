"""Atomic process coordinator for sanction finalisation side effects.

Dependency direction is intentionally top-down: this process imports the approval writer and the
legal-checklist module. Neither business owner imports the other.
"""

from sfpcl_credit.approvals.modules import approval_actions
from sfpcl_credit.legal_documents.modules import document_checklist


def approve_case(*, actor, case_id, payload, actor_permissions, request_meta=None):
    return approval_actions._approve_case_with_completion(
        actor=actor,
        case_id=case_id,
        payload=payload,
        actor_permissions=actor_permissions,
        request_meta=request_meta,
        completion=_create_document_checklist,
    )


def _create_document_checklist(
    *, actor, application_id, sanction_decision_id, request_meta=None
):
    document_checklist.refresh_for_approved_sanction(
        actor=actor,
        application_id=application_id,
        source_reason=f"approved_sanction_decision_created:{sanction_decision_id}",
        request_meta=request_meta,
    )
