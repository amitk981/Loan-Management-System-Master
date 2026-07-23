# Complete S02 Matrix

## Seven groups

| Group | Contract proof |
|---|---|
| Members | inherited 010N API/card/permission tests |
| Loan Applications | inherited 010N API/card/permission tests |
| Loan Accounts | inherited 010N API/card/permission tests |
| Documents | inherited 010N API/card/permission tests |
| Repayments | inherited 010N API/card/permission tests |
| Compliance Records | 011M3 canonical-type, role, leak, action, ordering, and pagination tests |
| Audit Logs | inherited restricted-authority 010N tests |

`GlobalSearchApiTests.test_returns_authorised_group_contract_and_default_empty_compliance_provider`
proves the exact seven-group response shape. 011M3 replaces only the registered compliance
provider; it does not move or weaken any inherited group/privacy seam.

## Fifteen source inputs

| Input | Existing focused proof |
|---|---|
| Borrower name | `test_all_source_inputs_map_to_the_scoped_member_root` |
| FPC name | same |
| Application reference | same |
| Loan account number | same |
| Folio number | same |
| Number of shares | same |
| PAN | same plus sensitive-authority/index tests |
| Aadhaar last four | same plus sensitive-authority/index tests |
| Mobile | same |
| Email | same |
| SAP customer code | same plus SAP-authority test |
| Cheque number | `test_sensitive_instrument_inputs_use_canonical_owner_tokens` |
| CDSL pledge sequence | same |
| SH-4 reference | same |
| Bank account last four | `test_all_source_inputs_map_to_the_scoped_member_root` plus index test |

## Card and pagination proof

- Every card retains the shared title, visible identifier, status, optional risk/amount, current
  owner, last-updated date/actor, and permission-filtered quick-action keys.
- Compliance controls/tasks/evidence, money-lending, Section 186, NBFC, and KYC/re-KYC are covered
  by `test_global_search_compliance.py`.
- `test_compliance_group_uses_shared_cap_and_independent_pagination` proves 21-row paging and opaque
  continuation reuse.
- `backend-final-focused-regressions.log` records 61 passing search/compliance reverse-consumer
  tests; `frontend-global-search-green.log` records grouped rendering/action coverage.

