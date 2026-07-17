from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json

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
from sfpcl_credit.configurations.modules.source_bank_governance import (
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
from sfpcl_credit.disbursements.modules.disbursement_scope import has_cfc_scope


@dataclass(frozen=True)
class CheckSpec:
    code: str
    label: str


@dataclass(frozen=True)
class InitiationReadinessDecision:
    loan_account_id: object
    loan_application_id: object
    ready_for_disbursement: bool
    blocker_error_code: str | None
    check_digest: str
    sap_customer_code_id: object | None
    sap_profile_request_id: object | None
    borrower_bank_account_id: object | None
    bank_verification_decision_id: object | None
    source_bank_account_id: object | None
    source_bank_governance_id: object | None
    source_bank_version_history_id: object | None
    source_bank_audit_log_id: object | None
    bank_cancelled_cheque_id: object | None = None
    bank_cancelled_cheque_document_id: object | None = None
    bank_cancelled_cheque_checksum_sha256: str | None = None
    bank_verifier_user_id: object | None = None
    bank_request_id: str | None = None
    bank_workflow_event_id: object | None = None
    bank_audit_log_id: object | None = None
    bank_version_history_id: object | None = None
    source_bank_request_id: str | None = None
    source_bank_facts_digest: str | None = None

    def safe_evidence(self):
        return {
            "check_digest": self.check_digest,
            "sap_customer_code_id": _string_or_none(self.sap_customer_code_id),
            "sap_profile_request_id": _string_or_none(self.sap_profile_request_id),
            "borrower_bank_account_id": _string_or_none(
                self.borrower_bank_account_id
            ),
            "bank_verification_decision_id": _string_or_none(
                self.bank_verification_decision_id
            ),
            "bank_cancelled_cheque_id": _string_or_none(
                self.bank_cancelled_cheque_id
            ),
            "bank_cancelled_cheque_document_id": _string_or_none(
                self.bank_cancelled_cheque_document_id
            ),
            "bank_cancelled_cheque_checksum_sha256": (
                self.bank_cancelled_cheque_checksum_sha256
            ),
            "bank_verifier_user_id": _string_or_none(self.bank_verifier_user_id),
            "bank_request_id": self.bank_request_id,
            "bank_workflow_event_id": _string_or_none(self.bank_workflow_event_id),
            "bank_audit_log_id": _string_or_none(self.bank_audit_log_id),
            "bank_version_history_id": _string_or_none(self.bank_version_history_id),
            "source_bank_account_id": _string_or_none(self.source_bank_account_id),
            "source_bank_governance_id": _string_or_none(
                self.source_bank_governance_id
            ),
            "source_bank_version_history_id": _string_or_none(
                self.source_bank_version_history_id
            ),
            "source_bank_audit_log_id": _string_or_none(
                self.source_bank_audit_log_id
            ),
            "source_bank_request_id": self.source_bank_request_id,
            "source_bank_facts_digest": self.source_bank_facts_digest,
        }


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
    """Return the redacted current pre-initiation projection without workflow writes."""
    result, _ = _evaluate(
        actor=actor, loan_account_id=loan_account_id, for_initiation=False
    )
    return result


def evaluate_for_initiation(*, actor, loan_account_id):
    """Return the narrow typed decision consumed by the payment workflow."""
    _, decision = _evaluate(
        actor=actor, loan_account_id=loan_account_id, for_initiation=True
    )
    return decision


def _evaluate(*, actor, loan_account_id, for_initiation):
    with transaction.atomic():
        account = resolve_readiness_account(
            actor=actor,
            loan_account_id=loan_account_id,
            cfc_scope_resolver=has_cfc_scope,
        )
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
        source_bank = resolve_source_bank_account(for_update=for_initiation)
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
        result = {
            "loan_account_id": str(account.loan_account_id),
            "loan_application_id": str(account.loan_application_id),
            "ready_for_disbursement": all(item["status"] == "pass" for item in checks),
            "evaluated_at": timezone.now().isoformat().replace("+00:00", "Z"),
            "checks": checks,
        }
        canonical_checks = [
            {"code": item["code"], "status": item["status"]} for item in checks
        ]
        check_digest = hashlib.sha256(
            json.dumps(canonical_checks, separators=(",", ":")).encode()
        ).hexdigest()
        decision = InitiationReadinessDecision(
            loan_account_id=account.loan_account_id,
            loan_application_id=account.loan_application_id,
            ready_for_disbursement=result["ready_for_disbursement"],
            blocker_error_code=_blocker_error_code(checks),
            check_digest=check_digest,
            sap_customer_code_id=sap.customer_code_id if sap_current else None,
            sap_profile_request_id=(
                getattr(sap, "profile_request_id", None) if sap_current else None
            ),
            borrower_bank_account_id=(
                getattr(bank, "bank_account_id", None) if bank.valid else None
            ),
            bank_verification_decision_id=(
                getattr(bank, "bank_verification_decision_id", None)
                if bank.valid
                else None
            ),
            bank_cancelled_cheque_id=(
                getattr(bank, "cancelled_cheque_id", None) if bank.valid else None
            ),
            bank_cancelled_cheque_document_id=(
                getattr(bank, "cancelled_cheque_document_id", None)
                if bank.valid
                else None
            ),
            bank_cancelled_cheque_checksum_sha256=(
                getattr(bank, "cancelled_cheque_checksum_sha256", None)
                if bank.valid
                else None
            ),
            bank_verifier_user_id=(
                getattr(bank, "verifier_user_id", None) if bank.valid else None
            ),
            bank_request_id=(getattr(bank, "request_id", None) if bank.valid else None),
            bank_workflow_event_id=(
                getattr(bank, "workflow_event_id", None) if bank.valid else None
            ),
            bank_audit_log_id=(
                getattr(bank, "audit_log_id", None) if bank.valid else None
            ),
            bank_version_history_id=(
                getattr(bank, "version_history_id", None) if bank.valid else None
            ),
            source_bank_account_id=(
                getattr(source_bank, "source_bank_account_id", None)
                if source_bank and source_bank.active
                else None
            ),
            source_bank_governance_id=(
                getattr(source_bank, "governance_id", None)
                if source_bank and source_bank.active
                else None
            ),
            source_bank_version_history_id=(
                getattr(source_bank, "version_history_id", None)
                if source_bank and source_bank.active
                else None
            ),
            source_bank_audit_log_id=(
                getattr(source_bank, "audit_log_id", None)
                if source_bank and source_bank.active
                else None
            ),
            source_bank_request_id=(
                getattr(source_bank, "request_id", None)
                if source_bank and source_bank.active
                else None
            ),
            source_bank_facts_digest=(
                getattr(source_bank, "source_facts_digest", None)
                if source_bank and source_bank.active
                else None
            ),
        )
        return result, decision


class DisbursementReadinessModule:
    evaluate = staticmethod(evaluate)
    evaluate_for_initiation = staticmethod(evaluate_for_initiation)


def _string_or_none(value):
    return str(value) if value else None


def _blocker_error_code(checks):
    failed = {item["code"] for item in checks if item["status"] == "fail"}
    categories = (
        (
            {
                "sanction_approved",
                "exception_approval_complete",
                "general_meeting_approval_complete",
                "appraisal_complete",
            },
            "APPROVAL_PENDING",
        ),
        (
            {
                "documentation_complete",
                "company_secretary_approval",
                "credit_manager_approval",
                "sanction_committee_approval",
                "term_sheet_complete",
                "loan_agreement_complete",
                "signature_mismatch_resolved",
            },
            "DOCUMENTATION_INCOMPLETE",
        ),
        (
            {
                "security_package_complete",
                "poa_complete",
                "sh4_complete",
                "cdsl_pledge_complete",
                "blank_dated_cheque_received",
            },
            "SECURITY_PACKAGE_INCOMPLETE",
        ),
        ({"sap_customer_code_present"}, "SAP_CUSTOMER_CODE_REQUIRED"),
        (
            {
                "cancelled_cheque_verified",
                "bank_account_verified",
                "source_bank_account_configured",
            },
            "BANK_ACCOUNT_NOT_VERIFIED",
        ),
        ({"amount_within_sanction"}, "DISBURSEMENT_EXCEEDS_SANCTION"),
    )
    for codes, error_code in categories:
        if failed & codes:
            return error_code
    return "INVALID_STATE_TRANSITION" if failed else None


__all__ = [
    "DisbursementReadinessModule",
    "InitiationReadinessDecision",
    "evaluate",
    "evaluate_for_initiation",
]
