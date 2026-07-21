# Slice 010N2: Epic 010 Terminal Servicing Recurrence Repair

## Status
Complete

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- CR-015

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Architecture Review Recurrence Repair
- Epic: 010
- Root ID: ROOT-010-REMINDER-DELIVERY-OWNER
- Terminal finalizer: CR-015-epic-010-terminal-servicing-owner-finalizer
- Repair attempt: 1

## Goal
Perform the one owner-authorized repair of the CR-015 terminal contract: restore cutoff-valid MIS
truth and replace the finalizer's remaining private/incomplete acceptance seam without regressing
the already-closed reminder provider owner.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/mis-owner-recurrence.log | AC-E10-R1, AC-E10-R2 |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/servicing-seam-recurrence.log | AC-E10-R3, AC-E10-R4, AC-E10-R5 |

## Source References
- `docs/slices/CR-015-epic-010-terminal-servicing-owner-finalizer.md` complete terminal contract
- `docs/source/functional-spec.md` M10-FR-003–010 and BR-066–074
- `docs/source/api-contracts.md` §§28–34 and 45
- `docs/source/data-model.md` §§18–20 and 34–35
- `docs/source/codebase-design.md` §§17.3, 26, 38, and 42

## Concrete Requirements
1. Preserve every CR-015 decision/side-effect owner and correct historical invoice admission using
   the real immutable `InterestInvoice.generated_at` plus `issued_at` lifecycle. Before, exactly-on,
   and after-cutoff invoice generation/issuance must project `not_generated`, `draft`, or `issued`
   from one retained source decision without consulting nonexistent or mutable aliases.
2. Complete the CR-015 cutoff matrix for account, reminder, repayment/reversal, DPD, disbursement,
   capitalisation, and invoice transitions. Exact MIS replay must retain one authorised immutable
   snapshot after every later mutation and concurrent writer interleaving.
3. Replace every cross-`TestCase.setUp()` dependency in the CR-015 acceptance classes with public
   builders. Recreate the promised partial-step repayment replay/concurrency/conflict, concurrent
   statement, safe empty/nonempty borrower export, and portal/reminder 1/100/101 matrices through
   public API or module seams with substantive state/effect assertions.
4. Replay the exact commands in both current recurrence logs and every original CR-015 review
   reproducer; current-run evidence must show each exact command GREEN. Do not substitute a narrower
   proxy, remove an acceptance ID, or weaken the five-case PostgreSQL contract.
5. Keep the closed reminder provider-effect root green under repayment, scope/source change,
   competing worker, retry, and timeout races. This repair is the same terminal contract, not a new
   corrective generation, provider policy, financial rule, or second finalizer.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer.Epic010TerminalOwnerFinalizerPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-E10-R1] Real-model before/on/after invoice lifecycle tests prove post-cutoff generated rows are
  absent and pre-cutoff draft/issued rows retain the exact cutoff-valid status.
- [AC-E10-R2] Complete mutable-source and concurrent-writer matrices leave MIS rows and exact replay
  authorised, immutable, and cutoff coherent.
- [AC-E10-R3] Public builders replace every touched cross-test setup dependency, and the original
  direct-repayment crash/replay probe plus zero/changed/concurrent effect matrices pass.
- [AC-E10-R4] Concurrent statement, borrower-safe CSV, approved instruction, and portal/reminder
  1/100/101 tests prove complete truthful projections with no silent truncation.
- [AC-E10-R5] All original and recurrence commands are retained GREEN, the exact PostgreSQL class
  passes twice, the closed reminder owner does not regress, and complete independent gates pass.

## Risk Level
High

