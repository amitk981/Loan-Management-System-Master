# Slice CR-015: Epic 010 Terminal Servicing Owner Finalizer

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010MA

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Architecture Review Finalizer
- Epic: 010
- Root ID: ROOT-010-REMINDER-DELIVERY-OWNER
- Exhausted corrective generation: 2

## Origin
Terminal architecture-review correction admitted by run
`2026-07-21_134356_architecture_review` after 010K3 reproduced the reminder root at ordinary
generation 2. The same final owner boundary groups the related MIS and servicing workflow roots.

## Goal
Retain one server-owned, replayable decision at every remaining Epic 010 financial side-effect and
historical-read boundary so reminder delivery, MIS cutoff truth, direct repayment, statements, and
portal collections cannot diverge across retries, races, or page boundaries.

## Depends-On Contract
010MA supplies the production servicing transports and UI entry points; 010K2, 010K3, and 010L
supply statement, as-of, reminder, and portal behavior. Preserve their public contracts while
replacing the unowned check/action gaps. 010MB and Epic 011 default opening may not consume Epic 010
truth until this finalizer completes.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/reminder-owner.log | AC-E10-F-1 |
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/mis-owner.log | AC-E10-F-2 |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | .ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/servicing-seam.log | AC-E10-F-3, AC-E10-F-4, AC-E10-F-5 |

## Source References
- `docs/source/functional-spec.md` M10-FR-003–010 and BR-066–074
- `docs/source/api-contracts.md` §§28–34 and 45
- `docs/source/data-model.md` §§18–20 and 34–35
- `docs/source/codebase-design.md` §§17.3, 26, 38, and 42
- `docs/source/screen-spec.md` S43–S46 and MP17–MP18
- `docs/slices/010K2-loan-ledger-statements-and-export.md`
- `docs/slices/010K3-servicing-as-of-owner-boundary-closure.md`
- `docs/slices/010L-member-portal-repayment-view.md`
- `docs/slices/010MA-servicing-account-and-repayment-frontend-wiring.md`

## Concrete Requirements
1. Replace the committed reminder pre-check/provider gap with one server-owned delivery claim and
   final serviceability proof. Repayment, scope revocation, changed current source, cancellation,
   retry, and competing workers must yield either one retained provider effect justified by that
   proof or zero provider calls; no stale serviceable decision may cross the adapter boundary.
2. Make quarterly MIS snapshot rows derive every mutable state from an immutable cutoff-valid owner
   decision. In particular, invoice issue/status, account status, reminders, repayment/reversal,
   DPD, disbursement, and capitalisation transitions after the cutoff cannot rewrite a subsequently
   generated historical report, while exact replay retains one authorised portfolio snapshot.
3. Replace the browser-owned capture/SAP/allocation sequence with one backend-owned direct-repayment
   command and retained step state. Exact retries resume or return the complete outcome after any
   crash boundary; changed-key/cross-account payloads conflict with zero extra effects; concurrent
   requests retain one capture, one SAP decision, one allocation, and one truthful response. The UI
   invokes only that command and never reports a partial attempt as complete.
4. Close the grouped servicing-read debt: statement request creation has one concurrent idempotency
   owner and one artifact; borrower CSV omits staff/internal servicing fields and retains safe
   statement metadata even when empty; portal collections traverse or expose canonical pagination
   without silent first-100 truncation. Availability and direct-repayment instructions come from a
   versioned, approved backend projection rather than mutable browser/config policy.
5. Replace cross-`TestCase.setUp` fixtures with public builders at the touched seams. Convert all
   three review probes to permanent regressions and add 1/100/101 reminder and portal matrices,
   before/cutoff/after MIS matrices, partial-step repayment replay, and concurrent statement cases.

## Scope Boundaries / Non-Goals
- No new repayment allocation rule, reminder content/cadence, MIS column, statement format, portal
  styling, interest formula, default behavior, or scheduler calendar.
- Reuse existing frontend components and visual patterns; this correction owns behavior and public
  transport only and requires component/service tests rather than an interactive visual gate.
- Do not reopen the closed DPD source owner; consume its public decision.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer.Epic010TerminalOwnerFinalizerPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-E10-F-1] Five PostgreSQL cases run twice and prove repayment-after-check, scope/source change,
  competing worker, retry, and provider-timeout reminder races retain at most one justified effect.
- [AC-E10-F-2] Before/cutoff/after source-transition matrices prove later invoice/status/reminder/
  repayment mutations cannot rewrite MIS history and exact replay remains authorised and immutable.
- [AC-E10-F-3] Capture, SAP, allocation, and response crash-boundary matrices prove the composite
  repayment command resumes exactly once and the frontend renders only the retained complete truth.
- [AC-E10-F-4] Concurrent statement replay yields one artifact; member CSV and empty metadata are
  safe; portal 1/100/101 collections are complete or explicitly paginated; approved/versioned
  instruction and action projections remain backend owned.
- [AC-E10-F-5] All review probes are permanent public-seam regressions; cross-test setup imports are
  removed from the touched acceptance classes; reverse consumers, permission/audit, typecheck,
  lint, build, complete suite, and coverage gates pass.

## Risk Level
High

## Done Checklist
- [ ] Impact analysis written before code
- [ ] Three failing review probes retained and converted to permanent regressions
- [ ] Reminder and MIS owner boundaries closed
- [ ] Composite repayment and servicing-read owners closed
- [ ] Five PostgreSQL acceptance tests pass twice
- [ ] Reverse-consumer and complete independent gates pass
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
