"""Read-only compliance provenance over recovery-owned evidence."""

from sfpcl_credit.recovery.models import RecoveryAction


def contains_document(*, source_id, document):
    row = RecoveryAction.objects.filter(pk=source_id).values(
        "initiation_evidence_document_ids_json", "completion_evidence_document_ids_json"
    ).first()
    return bool(row) and str(document.pk) in {
        *(str(value) for value in row["initiation_evidence_document_ids_json"]),
        *(str(value) for value in row["completion_evidence_document_ids_json"]),
    }
