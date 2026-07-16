# Repair Diagnosis

## Symptom

Independent backend coverage failed
`FinalDocumentationApprovalApiTests.test_disbursement_readiness_real_owners_reach_a126_then_all_pass`:
the readiness response also failed `sap_customer_code_present` instead of failing only the known
`source_bank_account_configured` A-126 blocker.

## Feedback Loop

The single named Django test reproduced the exact failure deterministically. Test execution took
0.397 seconds after database setup. See `evidence/terminal-logs/readiness-red.txt`.

## Root Cause

The pre-existing cross-owner readiness fixture invoked the SAP send and completion endpoints without
`X-Request-ID`. Slice 009B3C makes a public SAP decision contingent on exact sealed action evidence,
including traceable request context. The fixture therefore produced successful SAP rows whose audit
evidence was intentionally not eligible as current downstream truth.

## Repair

The fixture now supplies distinct request ids for its send and completion actions. This preserves
the stricter production predicate, the singular-ledger contract, and all public response behavior.
The exact test then passed, as did all 64 impacted SAP/current-evidence and readiness tests.
