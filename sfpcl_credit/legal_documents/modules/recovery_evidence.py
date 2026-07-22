from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.legal_documents.models import LoanDocument


def retain_recovery_evidence(*, application_id, document_ids, actor):
    """Attach actor-uploaded restricted files to the canonical loan file."""
    linked = set(
        LoanDocument.objects.filter(
            loan_application_id=application_id,
            document_id__in=document_ids,
            document_category__in={"recovery", "security"},
            generation_status="generated",
        ).values_list("document_id", flat=True)
    )
    missing = set(document_ids) - linked
    uploads = DocumentFile.objects.filter(
        pk__in=missing,
        uploaded_by_user=actor,
        sensitivity_level__in={"confidential", "restricted"},
    )
    if set(uploads.values_list("pk", flat=True)) != missing:
        return False
    for document in uploads:
        LoanDocument.objects.create(
            loan_application_id=application_id,
            document_type="recovery_action_evidence",
            document_category="recovery",
            document=document,
            output_format=(document.file_extension or "file")[:20],
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )
    return True
