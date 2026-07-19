# Bank Statement Contract Evidence

All examples use synthetic identifiers and amounts.

## Exact automatic match

Input CSV facts: exact normalized UTR, `125000.00`, receipt date, canonical loan-account number,
and narration containing that account number.

```json
{
  "line_count": 1,
  "matched_count": 1,
  "unmatched_count": 0,
  "exception_count": 0,
  "lines": [
    {
      "line_number": 1,
      "amount": "125000.00",
      "parse_status": "parsed",
      "match_status": "matched",
      "match_reason_code": "exact_reference_amount_date_account"
    }
  ]
}
```

Permanent proof:
`sfpcl_credit.tests.test_bank_statement_matching_api.BankStatementMatchingApiTests.test_exact_statement_evidence_matches_one_receipt_without_financial_mutation`.
The assertion snapshots account and schedule rows and proves zero allocation/ledger rows.

## Safe queue reasons

- `missing_reference`
- `missing_loan_reference`
- `missing_borrower_or_application_narration`
- `no_exact_receipt_candidate`
- `parse_failed`
- `counterpart_already_matched`
- `ambiguous_receipt_candidates` (defensive singularity guard)

Queue projections expose ids, dates, amount, parse/match status, safe reason code, and linked receipt
evidence only. They omit raw narration, raw bank reference, manual reason text, and file bytes.

## Manual match and uniqueness

```json
{
  "match_status": "matched",
  "match_reason_code": "authorised_manual_evidence_match",
  "repayment_evidence": {
    "bank_statement_line_id": "<synthetic-line-uuid>",
    "statement_match_status": "manual_match_exception",
    "allocation_status": "pending"
  }
}
```

Permanent SQLite/API proof:
`BankStatementMatchingApiTests.test_manual_match_requires_reason_and_one_receipt_cannot_be_consumed_twice`.
Database one-to-one/unique fields independently bind one line and one receipt. The declared
PostgreSQL proof is
`BankStatementMatchingPostgreSQLAcceptanceTests.test_concurrent_manual_matches_retain_one_statement_counterpart`;
local SQLite collection skipped it, and the orchestrator owns the twice-run PostgreSQL result.

## Audit and permission evidence

- File storage: `bank_statement.file_stored`, document id/sensitivity/workflow scope only.
- Import: `bank_statement.imported`, safe counts/ids/status and actor/roles.
- Automatic match: `bank_statement.line_auto_matched`, safe ids/code/time and actor/roles.
- Manual match: `bank_statement.line_manually_matched`, safe ids/code/time and actor/roles.
- Exception: `bank_statement.line_exception_recorded`, safe id/code/time and actor/roles.
- Raw narration, bank reference, and manual reason are absent from these reconciliation audits.
- Anonymous, role/permission-ineligible, out-of-scope receipt, invalid file, changed replay, and
  already-consumed counterpart tests all assert zero reconciliation mutation.
