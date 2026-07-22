"""Governed retained-document adapter for a formal Non-Payment Note."""

from io import BytesIO
from textwrap import wrap

from django.core.files.base import ContentFile

from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents.models import LoanDocument


def generate_non_payment_note_document(
    *, note_id, loan_application_id, actor, facts, storage=None
):
    storage = storage or LocalDocumentStorage()
    content = _render_pdf(facts)
    file_name = f"non-payment-note-{note_id}.pdf"
    stored = storage.store(ContentFile(content, name=file_name))
    try:
        document_file = DocumentFile.objects.create(
            file_name=file_name,
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=actor,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )
        loan_document = LoanDocument.objects.create(
            loan_application_id=loan_application_id,
            document_type="non_payment_note",
            document_category="recovery",
            document=document_file,
            output_format="pdf",
            generation_status=LoanDocument.GENERATION_GENERATED,
            execution_status=LoanDocument.EXECUTION_PENDING,
            verification_status=LoanDocument.VERIFICATION_PENDING,
        )
        AuditLog.objects.create(
            actor_user=actor,
            action="documents.loan_document.generated",
            entity_type="loan_document",
            entity_id=loan_document.pk,
            new_value_json={
                "document_type": "non_payment_note",
                "document_id": str(document_file.pk),
                "checksum_sha256": document_file.checksum_sha256,
                "non_payment_note_id": str(note_id),
            },
        )
        return loan_document
    except Exception:
        storage.delete(stored)
        raise


def _render_pdf(facts):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4, invariant=1)
    width, height = A4
    y = height - 54
    pdf.setTitle("Formal Non-Payment Note")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(54, y, "Formal Non-Payment Note")
    y -= 28
    pdf.setFont("Helvetica", 9)
    lines = [
        ("Default case", facts["default_case_id"]),
        ("Loan account", facts["loan_account_id"]),
        ("Borrower", facts["borrower_name"]),
        ("Original due date", facts["original_due_date"]),
        ("Grace period ended", facts["grace_period_end_date"]),
        ("Grace outcome", facts["grace_outcome_summary"]),
        ("Extension ended", facts["extension_end_date"]),
        ("Extension outcome", facts["extension_outcome_summary"]),
        ("Extension reason", facts["extension_reason"]),
        ("Source assessment classification", facts["source_assessment_classification"]),
        ("Source assessment reason", facts["source_assessment_reason"]),
        ("Principal outstanding", facts["outstanding_principal_amount"]),
        ("Interest outstanding", facts["outstanding_interest_amount"]),
        ("Intentionality assessment", facts["intentionality_assessment"]),
        ("Reason for non-payment", facts["reason_for_non_payment"]),
        ("Recommendation", facts["recommended_recovery_action"]),
        ("Evidence reviewed", ", ".join(facts["evidence_document_ids"])),
        ("Prepared by", facts["prepared_by"]),
        ("Reviewed by", facts["reviewed_by"]),
        ("Submitted at", facts["submitted_at"]),
    ]
    for label, value in lines:
        wrapped = wrap(f"{label}: {value}", width=105) or [f"{label}:"]
        for line in wrapped:
            if y < 54:
                pdf.showPage()
                pdf.setFont("Helvetica", 9)
                y = height - 54
            pdf.drawString(54, y, line)
            y -= 14
        y -= 3
    pdf.save()
    return output.getvalue()
