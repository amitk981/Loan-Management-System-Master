"""Legal-document-owned target authority for Stage 4 mutations."""

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import LoanDocument


DOCUMENTATION_MUTATION_ROLES = {"compliance_team_member", "company_secretary"}


class AccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code


class NotFound(Exception):
    pass


class ProvenanceConflict(Exception):
    pass


class RoleAuthorityDenied(Exception):
    pass


def require_mutation_actor(*, actor, permission):
    permissions = auth_service.effective_permission_codes(actor)
    if (
        not actor.can_authenticate()
        or permission not in permissions
        or not DOCUMENTATION_MUTATION_ROLES.intersection(actor.role_codes())
    ):
        raise AccessDenied


def require_company_secretary(actor):
    if "company_secretary" not in actor.role_codes():
        raise RoleAuthorityDenied


def require_compliance_preparer(actor):
    if "compliance_team_member" not in actor.role_codes():
        raise RoleAuthorityDenied


def resolve_current_stage4_target(
    *, actor, permission, loan_document_id, for_update=False
):
    """Resolve the sanctioned documentation queue before owner/evidence queries.

    Auth §19.2 defines sanctioned documentation applications as the canonical object scope for
    Compliance Team and Company Secretary actors. The permission remains action-specific.
    """
    require_mutation_actor(actor=actor, permission=permission)
    queryset = LoanDocument.objects
    if for_update:
        queryset = queryset.select_for_update(of=("self",))
    loan_document = (
        queryset.select_related("document", "loan_application")
        .filter(pk=loan_document_id)
        .first()
    )
    if loan_document is None:
        raise NotFound
    if (
        loan_document.loan_application.application_status
        != LoanApplication.STATUS_APPROVED_BY_SANCTION
    ):
        raise AccessDenied("OBJECT_ACCESS_DENIED")
    if (
        loan_document.renderer_validation_status
        != LoanDocument.RENDERER_CURRENT_VALIDATED
    ):
        raise ProvenanceConflict
    return loan_document
