# Sanitized Disbursement Readiness Examples

## Ready owner-decision contract

```json
{
  "success": true,
  "data": {
    "loan_account_id": "10000000-0000-0000-0000-000000000001",
    "loan_application_id": "20000000-0000-0000-0000-000000000002",
    "ready_for_disbursement": true,
    "evaluated_at": "2026-07-16T08:00:00Z",
    "checks": [
      {"code": "sanction_approved", "label": "Sanction approved", "status": "pass"},
      {"code": "loan_account_sanctioned", "label": "Loan account is sanctioned", "status": "pass"},
      {"code": "exception_approval_complete", "label": "Exception approval complete", "status": "pass"},
      {"code": "general_meeting_approval_complete", "label": "General meeting approval complete", "status": "pass"},
      {"code": "kyc_complete", "label": "KYC complete", "status": "pass"},
      {"code": "appraisal_complete", "label": "Appraisal complete", "status": "pass"},
      {"code": "documentation_complete", "label": "Documentation checklist complete", "status": "pass"},
      {"code": "company_secretary_approval", "label": "Company Secretary checklist approval", "status": "pass"},
      {"code": "credit_manager_approval", "label": "Credit Manager checklist approval", "status": "pass"},
      {"code": "sanction_committee_approval", "label": "Sanction Committee checklist approval", "status": "pass"},
      {"code": "security_package_complete", "label": "Security package complete", "status": "pass"},
      {"code": "poa_complete", "label": "Power of Attorney complete", "status": "pass"},
      {"code": "term_sheet_complete", "label": "Term Sheet complete", "status": "pass"},
      {"code": "loan_agreement_complete", "label": "Loan Agreement complete", "status": "pass"},
      {"code": "sh4_complete", "label": "SH-4 complete when applicable", "status": "pass"},
      {"code": "cdsl_pledge_complete", "label": "CDSL pledge complete when applicable", "status": "pass"},
      {"code": "blank_dated_cheque_received", "label": "Blank-dated cheque received", "status": "pass"},
      {"code": "cancelled_cheque_verified", "label": "Cancelled cheque verified", "status": "pass"},
      {"code": "bank_account_verified", "label": "Borrower bank account verified", "status": "pass"},
      {"code": "signature_mismatch_resolved", "label": "Signature mismatch resolved", "status": "pass"},
      {"code": "sap_customer_code_present", "label": "SAP customer code present", "status": "pass"},
      {"code": "source_bank_account_configured", "label": "Source bank account configured", "status": "pass"},
      {"code": "amount_within_sanction", "label": "Disbursement amount within sanction", "status": "pass"}
    ]
  }
}
```

This exact public passing shape is exercised with bounded fake owner decisions. Production remains
honestly blocked on `source_bank_account_configured` under A-126 until governance supplies that owner.

## Representative blocked item

```json
{
  "code": "source_bank_account_configured",
  "label": "Source bank account configured",
  "status": "fail",
  "reason": "No governed active source bank account is configured."
}
```

The all-blocked test asserts all 23 items, their exact order, a reason for every failure, no secret
fragments, and zero audit/workflow writes from the GET.
