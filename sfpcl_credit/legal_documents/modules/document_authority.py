"""Legal-document-owned target authority for Stage 4 mutations."""

from django.db.models import F

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.models import AuditLog
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


def has_terminal_execution_consumption(loan_document):
    """Return immutable legal-owner truth that an execution consumer froze this document."""
    return AuditLog.objects.filter(
        action="documents.execution.consumed",
        entity_type="loan_document",
        entity_id=loan_document.pk,
    ).exists()


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


def resolve_current_stage4_signature(
    *, actor, permission, signature_record_id, for_update=False
):
    """Resolve an accessible Stage-4 parent and signature as one nondisclosing lookup."""
    from sfpcl_credit.legal_documents.models import SignatureRecord

    require_mutation_actor(actor=actor, permission=permission)
    queryset = SignatureRecord.objects
    if for_update:
        queryset = queryset.select_for_update(of=("self", "loan_document"))
    signature = (
        queryset.select_related(
            "loan_document__loan_application",
            "mismatch_resolution_document",
        )
        .filter(
            pk=signature_record_id,
            loan_document__loan_application__application_status=(
                LoanApplication.STATUS_APPROVED_BY_SANCTION
            ),
            loan_document__renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            loan_document__document__isnull=False,
            loan_document__renderer_validated_document_id=F(
                "loan_document__document_id"
            ),
            loan_document__renderer_validated_checksum_sha256=F(
                "loan_document__document__checksum_sha256"
            ),
        )
        .first()
    )
    if signature is None:
        raise NotFound
    return signature
