"""Document-owned NOC generation evidence facade."""

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal

from django.db import models
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents.models import LoanDocument


NOC_MERGE_FIELDS = frozenset(
    {
        "borrower_name",
        "loan_account_number",
        "application_reference",
        "disbursed_amount",
        "full_repayment_date",
        "issued_by",
        "issue_date",
    }
)


@dataclass(frozen=True)
class GeneratedNocEvidence:
    loan_document_id: object
    document_id: object
    generation_audit_id: object
    document_template_id: object
    document_template_version: str
    renderer_contract_version: str
    renderer_validated_checksum_sha256: str
    merge_values_sha256: str


def resolve_generated_noc_evidence(
    *, application_id, document_id, canonical_facts, signatory
):
    row = (
        LoanDocument.objects.select_related("document", "document_template")
        .filter(
            document_id=document_id,
            loan_application_id=application_id,
            document_type="noc",
            document_category="closure",
            generation_status=LoanDocument.GENERATION_GENERATED,
            document__isnull=False,
            document_template__isnull=False,
            document_template__document_type="noc",
            document_template__approval_status="approved",
            document_template__effective_from__lte=timezone.localdate(),
        )
        .filter(
            models.Q(document_template__effective_to__isnull=True)
            | models.Q(document_template__effective_to__gte=timezone.localdate())
        )
        .first()
    )
    if (
        row is None
        or row.renderer_validation_status != LoanDocument.RENDERER_CURRENT_VALIDATED
        or set(row.document_template.merge_fields_json or []) != NOC_MERGE_FIELDS
    ):
        return None
    merge_values = {
        "borrower_name": canonical_facts["borrower_name"],
        "loan_account_number": canonical_facts["loan_account_number"],
        "application_reference": canonical_facts["application_reference"],
        "disbursed_amount": f"{Decimal(canonical_facts['disbursed_amount']):.2f}",
        "full_repayment_date": canonical_facts["full_repayment_date"],
        "issued_by": signatory.full_name,
        "issue_date": timezone.localdate().isoformat(),
    }
    merge_digest = hashlib.sha256(
        json.dumps(merge_values, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    audit = AuditLog.objects.filter(
        action="documents.loan_document.generated",
        entity_type="loan_document",
        entity_id=row.pk,
        actor_user=signatory,
        new_value_json__document_id=str(row.document_id),
        new_value_json__document_template_id=str(row.document_template_id),
        new_value_json__renderer_contract_version=row.renderer_contract_version,
        new_value_json__renderer_validated_checksum_sha256=(
            row.renderer_validated_checksum_sha256
        ),
        new_value_json__merge_field_names=sorted(NOC_MERGE_FIELDS),
        new_value_json__merge_values_sha256=merge_digest,
    ).first()
    if audit is None:
        return None
    return GeneratedNocEvidence(
        loan_document_id=row.pk,
        document_id=row.document_id,
        generation_audit_id=audit.pk,
        document_template_id=row.document_template_id,
        document_template_version=row.document_template.template_version,
        renderer_contract_version=row.renderer_contract_version,
        renderer_validated_checksum_sha256=row.renderer_validated_checksum_sha256,
        merge_values_sha256=merge_digest,
    )


__all__ = ["GeneratedNocEvidence", "NOC_MERGE_FIELDS", "resolve_generated_noc_evidence"]
