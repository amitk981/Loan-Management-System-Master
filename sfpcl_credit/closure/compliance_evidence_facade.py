"""Read-only compliance provenance over archive-owned evidence."""

from sfpcl_credit.closure.models import ArchiveRecord


def contains_document(*, source_id, document):
    return ArchiveRecord.objects.filter(
        pk=source_id, file_location_digital=document.storage_key
    ).exists()
