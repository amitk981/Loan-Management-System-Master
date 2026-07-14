from dataclasses import dataclass

from sfpcl_credit.approvals.models import SanctionDecision


@dataclass(frozen=True)
class SanctionDocumentFacts:
    borrower_name: str | None
    nominee_name: str | None
    witness_name: str | None
    shares_held: int | None
    purpose: str | None
    loan_amount: str | None
    sanctioned_tenure_months: int | None
    interest_rate_type: str | None
    interest_rate_value: str | None
    repayment_date: object | None
    penal_interest_rate: str | None
    charges: dict
    security: str | None
    dispute_resolution: str | None


def resolve_for_generation(*, application_id):
    decision = (
        SanctionDecision.objects.select_related("approval_case")
        .filter(loan_application_id=application_id, decision="sanctioned")
        .first()
    )
    if decision is None:
        return None
    review = decision.approval_case.appraisal_facts_json or {}
    borrower = review.get("borrower") or {}
    nominee = review.get("nominee") or {}
    witness = review.get("witness") or {}
    shareholding = review.get("shareholding") or {}
    purpose = review.get("purpose") or {}
    return SanctionDocumentFacts(
        borrower_name=borrower.get("name"),
        nominee_name=nominee.get("name"),
        witness_name=witness.get("name"),
        shares_held=shareholding.get("number_of_shares"),
        purpose=purpose.get("description"),
        loan_amount=(
            f"{decision.sanctioned_amount:.2f}"
            if decision.sanctioned_amount is not None
            else None
        ),
        sanctioned_tenure_months=decision.sanctioned_tenure_months,
        interest_rate_type=decision.interest_rate_type or None,
        interest_rate_value=(
            f"{decision.interest_rate_value:.4f}"
            if decision.interest_rate_value is not None
            else None
        ),
        repayment_date=decision.repayment_date,
        penal_interest_rate=(
            f"{decision.penal_interest_rate:.4f}"
            if decision.penal_interest_rate is not None
            else None
        ),
        charges=decision.charges_json or {},
        security=decision.security_required_summary or None,
        dispute_resolution=decision.conditions_precedent or None,
    )
