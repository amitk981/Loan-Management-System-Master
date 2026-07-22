"""Read-only compliance provenance over stamp-duty-owned evidence."""

from sfpcl_credit.legal_documents.models import StampDutyRecord


def contains_document(*, source_id, document):
    return StampDutyRecord.objects.filter(
        pk=source_id, loan_document__document=document, status="adequate"
    ).exists()
