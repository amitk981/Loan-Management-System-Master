from dataclasses import dataclass

from sfpcl_credit.applications.models import LoanApplication


@dataclass(frozen=True)
class ApplicationDocumentFacts:
    application_id: object
    application_reference_number: str | None
    application_status: str
    borrower_type: str


def resolve_for_generation(*, application_id, for_update=False):
    queryset = LoanApplication.objects.all()
    if for_update:
        queryset = queryset.select_for_update(of=("self",))
    application = queryset.filter(loan_application_id=application_id).first()
    if application is None:
        return None
    return ApplicationDocumentFacts(
        application_id=application.pk,
        application_reference_number=application.application_reference_number,
        application_status=application.application_status,
        borrower_type=application.borrower_type,
    )


def sanctioned_status():
    return LoanApplication.STATUS_APPROVED_BY_SANCTION
