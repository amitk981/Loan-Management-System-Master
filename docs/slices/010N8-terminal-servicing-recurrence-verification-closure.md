# Slice 010N8: Terminal Servicing Recurrence Verification Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010N5

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Architecture Review Recurrence Repair
- Epic: 010
- Root ID: ROOT-010-REMINDER-DELIVERY-OWNER
- Terminal finalizer: CR-015-epic-010-terminal-servicing-owner-finalizer
- Repair attempt: 1

## Goal
Finish the existing CR-015 repair episode with public-owner evidence for MIS cutoff replay and
reminder source delivery, and make the staff client accept only a complete, relationally coherent
backend-owned direct-repayment result.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | .ralph/runs/2026-07-22_055158_architecture_review/evidence/review-probes/mis-public-owner-closure.log | AC-E10-RV1 |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | .ralph/runs/2026-07-22_055158_architecture_review/evidence/review-probes/reminder-source-owner-closure.log | AC-E10-RV2 |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | .ralph/runs/2026-07-22_055158_architecture_review/evidence/review-probes/servicing-composite-contract.log | AC-E10-RV3, AC-E10-RV4 |

## Source References
- `docs/slices/CR-015-epic-010-terminal-servicing-owner-finalizer.md` requirements 1–5
- `docs/slices/010N2-epic-010-terminal-servicing-recurrence-repair.md` requirements 1–5
- `docs/slices/010N5-terminal-servicing-recurrence-owner-closure.md` requirements 1–4
- `docs/working/API_CONTRACTS.md` “Epic 010 terminal servicing owner contracts”
- `docs/source/codebase-design.md` §§17.1–17.2, 26, and 42

## Concrete Requirements
1. Replace helper-only MIS closure proof with a real-model public owner matrix. Generate the Q1
   report through the public MIS API for invoices generated before, on, and after the cutoff and
   issued before, on, and after it; mutate each source after generation, then prove detail,
   drill-down, exports, and exact idempotent replay retain one byte-stable cutoff-valid snapshot.
2. Isolate every reminder serviceability cause in the trusted five-case class. The recipient-source
   case changes only the retained SMS/email source and asserts zero provider calls; scope revocation
   is a separate cause. Every repayment/source/worker/retry/timeout case must assert the exact
   provider-effect count and retained delivery state without one cause masking another.
3. Validate the complete direct-repayment response at the service boundary before casting or
   rendering it. Require every declared capture, SAP-posting, allocation, allocation-rule, amount,
   and loan-balance field; bind capture to the requested loan, allocation to that capture, and all
   monetary/status fields to their documented types. Unknown, missing, null, or cross-owner truth
   fails visibly after the sole composite request.
4. Complete the backend public-command matrix across capture, SAP-posting, allocation, and retained-
   response crash points. Exact retry and equal-key concurrency must return one complete outcome and
   retain exactly one receipt, SAP decision, allocation, ledger/balance effect, and audit trail;
   changed payload/account binding must conflict with zero extra effects.
5. Replay the original CR-015, recurrence, 010N5, and current review commands exactly. Convert the
   current probes to permanent public-seam regressions, preserve the same three Finding ID/Root ID
   pairs, and do not weaken the five-test PostgreSQL count or grouped terminal contract.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer.Epic010TerminalOwnerFinalizerPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-E10-RV1] Public MIS generation, detail, drill-down, export, and exact replay prove the real
  before/on/after invoice lifecycle remains cutoff coherent after every later source mutation.
- [AC-E10-RV2] Five isolated repayment/source/worker/retry/timeout cases pass twice on PostgreSQL and
  assert at most one justified provider effect without scope or source causes masking one another.
- [AC-E10-RV3] Identifier-only, incomplete, null, unknown-field, wrong-type, cross-loan, and cross-
  repayment composite responses all fail visibly after one request; complete and replayed responses
  retain the documented full shape and no client-owned financial substep.
- [AC-E10-RV4] Public crash/retry/conflict/concurrency matrices retain one complete backend outcome,
  one receipt, one SAP decision, one allocation, one ledger/balance effect, and one audit trail, with
  every inherited and current reproducer green.

## Risk Level
High
