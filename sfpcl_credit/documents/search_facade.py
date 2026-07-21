"""Document search rows constrained by canonical application visibility."""

from django.db.models import Q

from sfpcl_credit.applications.models import ApplicationDocument
from sfpcl_credit.legal_documents.models import LoanDocument


READ_PERMISSION = "documents.loan_document.read"


def matching_documents(*, permissions, query, application_ids, limit):
    if READ_PERMISSION not in permissions:
        return [], frozenset()
    application_documents = list(
        ApplicationDocument.objects.select_related(
            "loan_application", "loan_application__member", "document_file",
            "created_by_user", "updated_by_user",
        )
        .filter(loan_application_id__in=application_ids)
        .filter(Q(document_file__file_name__istartswith=query) | Q(loan_application_id__in=application_ids))
        .order_by("-created_at", "-application_document_id")[:limit]
    )
    loan_documents = list(
        LoanDocument.objects.select_related(
            "loan_application", "loan_application__member", "document", "verified_by_user",
        )
        .filter(loan_application_id__in=application_ids)
        .filter(Q(document__file_name__istartswith=query) | Q(loan_application_id__in=application_ids))
        .order_by("-created_at", "-loan_document_id")[:limit]
    )
    ids = {row.application_document_id for row in application_documents}
    ids.update(row.loan_document_id for row in loan_documents)
    return (application_documents, loan_documents), frozenset(ids)


__all__ = ["matching_documents"]
