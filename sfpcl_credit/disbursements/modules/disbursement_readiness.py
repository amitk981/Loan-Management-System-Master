from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.modules.document_checklist_facts import (
    resolve_blank_cheque_bank_fact,
)
from sfpcl_credit.approvals.modules.disbursement_readiness import (
    resolve_approval_readiness,
)
from sfpcl_credit.legal_documents.modules.disbursement_readiness import (
    resolve_legal_readiness,
)
from sfpcl_credit.configurations.modules.configuration_resolver import (
    resolve_source_bank_account,
)
from sfpcl_credit.loans.modules.loan_account_lifecycle import (
    resolve_readiness_account,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    get_customer_code_for_member as resolve_sap_code,
)
from sfpcl_credit.processes.security_instrument_evidence import (
    terminal_checklist_evidence,
)
from sfpcl_credit.security_instruments.modules.disbursement_readiness import (
    resolve_security_readiness,
)


@dataclass(frozen=True)
class CheckSpec:
    code: str
    label: str


CHECK_SPECS = (
    CheckSpec("sanction_approved", "Sanction approved"),
    CheckSpec("loan_account_sanctioned", "Loan account is sanctioned"),
    CheckSpec("exception_approval_complete", "Exception approval complete"),
    CheckSpec("general_meeting_approval_complete", "General meeting approval complete"),
    CheckSpec("kyc_complete", "KYC complete"),
    CheckSpec("appraisal_complete", "Appraisal complete"),
    CheckSpec("documentation_complete", "Documentation checklist complete"),
    CheckSpec("company_secretary_approval", "Company Secretary checklist approval"),
    CheckSpec("credit_manager_approval", "Credit Manager checklist approval"),
    CheckSpec("sanction_committee_approval", "Sanction Committee checklist approval"),
    CheckSpec("security_package_complete", "Security package complete"),
    CheckSpec("poa_complete", "Power of Attorney complete"),
    CheckSpec("term_sheet_complete", "Term Sheet complete"),
    CheckSpec("loan_agreement_complete", "Loan Agreement complete"),
    CheckSpec("sh4_complete", "SH-4 complete when applicable"),
    CheckSpec("cdsl_pledge_complete", "CDSL pledge complete when applicable"),
    CheckSpec("blank_dated_cheque_received", "Blank-dated cheque received"),
    CheckSpec("cancelled_cheque_verified", "Cancelled cheque verified"),
    CheckSpec("bank_account_verified", "Borrower bank account verified"),
    CheckSpec("signature_mismatch_resolved", "Signature mismatch resolved"),
    CheckSpec("sap_customer_code_present", "SAP customer code present"),
    CheckSpec("source_bank_account_configured", "Source bank account configured"),
    CheckSpec("amount_within_sanction", "Disbursement amount within sanction"),
)


def _check(spec, passed, reason):
    item = {"code": spec.code, "label": spec.label, "status": "pass" if passed else "fail"}
    if not passed:
        item["reason"] = reason
    return item


def evaluate(*, actor, loan_account_id):
    """Return the current pre-initiation decision without writing workflow truth."""
    with transaction.atomic():
        account = resolve_readiness_account(actor=actor, loan_account_id=loan_account_id)
        approval = resolve_approval_readiness(
            application_id=account.loan_application_id,
            sanction_decision_id=account.sanction_decision_id,
        )
        legal = resolve_legal_readiness(
            application_id=account.loan_application_id,
            terminal_security_evidence=terminal_checklist_evidence,
        )
        completed_codes = legal.completed_item_codes
        security = resolve_security_readiness(
            application_id=account.loan_application_id,
            terminal_item_completed=completed_codes.__contains__,
        )
        bank = resolve_blank_cheque_bank_fact(
            application_id=account.loan_application_id
        )
        sap = resolve_sap_code(account.member_id, for_update=True)
        source_bank = resolve_source_bank_account()
        sap_current = bool(
            sap
            and account.sap_customer_code_id
            and sap.customer_code_id == account.sap_customer_code_id
            and sap.member_id == account.member_id
            and sap.loan_application_id == account.loan_application_id
            and sap.status == "active"
        )
        known = {
            "sanction_approved": (
                approval.sanction_approved and account.relationships_coherent,
                "The exact current terminal sanction is unavailable or incoherent.",
            ),
            "loan_account_sanctioned": (
                account.loan_account_status == "sanctioned",
                "The loan account is not in the sanctioned pre-initiation state.",
            ),
            "kyc_complete": (
                account.member_kyc_status == "verified",
                "Current borrower KYC is not verified.",
            ),
            "exception_approval_complete": (
                approval.exception_approval_complete,
                "Required exception approval is incomplete.",
            ),
            "general_meeting_approval_complete": (
                approval.general_meeting_approval_complete,
                "Required general meeting approval is incomplete.",
            ),
            "appraisal_complete": (
                approval.appraisal_complete,
                "The current approved appraisal is incomplete.",
            ),
            "documentation_complete": (
                legal.documentation_complete,
                "The current documentation checklist is incomplete.",
            ),
            "company_secretary_approval": (
                legal.company_secretary_approval,
                "Company Secretary checklist approval is missing or stale.",
            ),
            "credit_manager_approval": (
                legal.credit_manager_approval,
                "Credit Manager checklist approval is missing or stale.",
            ),
            "sanction_committee_approval": (
                legal.sanction_committee_approval,
                "Sanction Committee checklist approval is missing or stale.",
            ),
            "security_package_complete": (
                security.security_package_complete,
                "The current security package is incomplete.",
            ),
            "poa_complete": (
                security.poa_complete,
                "The current Power of Attorney is incomplete.",
            ),
            "term_sheet_complete": (
                legal.term_sheet_complete,
                "The current Term Sheet is not executed and verified.",
            ),
            "loan_agreement_complete": (
                legal.loan_agreement_complete,
                "The current Loan Agreement is not executed and verified.",
            ),
            "sh4_complete": (
                security.sh4_complete,
                "The applicable SH-4 custody path is incomplete.",
            ),
            "cdsl_pledge_complete": (
                security.cdsl_pledge_complete,
                "The applicable CDSL pledge path is incomplete.",
            ),
            "blank_dated_cheque_received": (
                security.blank_dated_cheque_received,
                "The blank-dated cheque has not reached verified custody.",
            ),
            "cancelled_cheque_verified": (
                getattr(bank, "cancelled_cheque_verified", bank.valid),
                "The current cancelled-cheque evidence is not verified.",
            ),
            "bank_account_verified": (
                getattr(bank, "bank_account_verified", bank.valid),
                "The current borrower bank account is not verified.",
            ),
            "signature_mismatch_resolved": (
                legal.signature_mismatch_resolved,
                "A current signature mismatch remains unresolved.",
            ),
            "sap_customer_code_present": (
                sap_current,
                "The account is not coherently bound to the current active SAP code.",
            ),
            "source_bank_account_configured": (
                bool(source_bank and source_bank.active),
                "No governed active source bank account is configured.",
            ),
            "amount_within_sanction": (
                Decimal("0") < account.disbursement_amount <= account.sanctioned_amount,
                "The proposed disbursement amount exceeds the current sanction.",
            ),
        }
        checks = []
        for spec in CHECK_SPECS:
            passed, reason = known.get(
                spec.code,
                (False, f"Current source evidence for {spec.label.lower()} is unavailable."),
            )
            checks.append(_check(spec, passed, reason))
        return {
            "loan_account_id": str(account.loan_account_id),
            "loan_application_id": str(account.loan_application_id),
            "ready_for_disbursement": all(item["status"] == "pass" for item in checks),
            "evaluated_at": timezone.now().isoformat().replace("+00:00", "Z"),
            "checks": checks,
        }


class DisbursementReadinessModule:
    evaluate = staticmethod(evaluate)


__all__ = ["CHECK_SPECS", "DisbursementReadinessModule", "evaluate"]
