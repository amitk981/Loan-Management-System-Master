# Slice 009H3B: Communications Dispatcher Crash and Race Closure

## Status
Superseded

## Superseded By

- 009H3BA
- 009H3BB

Failed run `2026-07-18_022416_normal_run` implemented the combined candidate successfully but
measured 2,118 changed lines against the configured 2,000-line limit. The dependency-ordered
successors preserve the complete scope below: 009H3BA owns the pre-provider dispatcher/outbox
boundary, and 009H3BB owns communications finalization plus public/race closure.

## Origin
Oversized slice: `009H3`

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Depends On
- 009H3A

## Goal
Move all remaining advice template/render/delivery/finalization policy behind the communications
dispatcher and close provider acceptance before local receipt/Communication retention with one
durable, race-safe outbox contract.

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/api-contracts.md` §§31.5, 39, and 45
- `docs/source/integrations.md` §§9-10, 19.3, and 21
- `docs/source/codebase-design.md` §§20.6, 22.2, 26.3, 36.2, 40.1-40.2, and 42.4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`
- Retained oversized run `.ralph/runs/2026-07-18_010406_normal_run/`

## Concrete Requirements
1. Make `communications.modules.communication_dispatcher` the single executable owner of approved/
   effective template resolution, exact declared-variable and sensitive-value validation,
   rendering, protected Communication creation, durable outbox/provider receipt, adapter dispatch,
   delivery status, and communication audit. Remove or reduce the legacy disbursements advice module
   to a policy-free boundary; do not leave duplicate template, rendering, receipt, or audit policy.
2. Keep disbursements as the owner of intent, authority, and immutable upstream financial context.
   It must supply the dispatcher a frozen advice context and consume an ordinary delivery decision;
   communications must not import disbursement models/modules or query financial policy directly.
3. Before any provider call, durably freeze and commit the stable advice intent/idempotency key plus
   canonical recipient, approved template/version/checksum, subject, body, related entity, and
   payload digest in the 009H3A outbox. Same key plus changed email, template provenance, subject,
   body, recipient, or entity conflicts before dispatch, including after a crash and with a fresh
   adapter. Exact retry reuses one logical provider identity.
4. Complete the Manual/Fake/Future contract through the dispatcher. Exact calls return one provider
   identity/status; provider rejection leaves the outbox pending and retryable; malformed provider
   results fail closed without sent/receipt/Communication truth. An accepted provider result can be
   finalized after a local failure without invoking a second logical external message.
5. Finalization must reconcile the locked current disbursement context and frozen outbox, then
   atomically retain exactly one communications-owned receipt, one protected Communication, one
   disbursement action, one safe communication audit, and one workflow event. Record every tested
   adapter result while concurrent losers remain clean and cannot retain partial success evidence.
6. Preserve every 009H2 role/scope rule, current-contact/template/upstream reconciliation, recipient
   masking, safe response/error contract, and exact replay behavior. General audit/workflow evidence
   must contain only masked/digested recipient and content/provider facts—never the raw email,
   rendered subject/body, full UTR, or sensitive bank content.
7. Preserve the public `POST /api/v1/disbursements/{id}/send-advice/` request/response/status contract
   unless source-required correction is unavoidable. Do not change money, transfer, loan-account,
   register, checklist, repayment, schedule, interest, default, closure, or borrower-portal truth.

## Test Cases
- Simulate provider acceptance followed separately by failure before receipt update and before final
  Communication commit. A fresh-adapter exact retry must retain one provider identity; changed
  payload, recipient/email, template provenance, subject/body, or entity must conflict before a
  second logical message or any changed final evidence.
- Five concurrent PostgreSQL callers run in two independently executed methods and record every
  adapter result. Each race retains one external message identity, one frozen outbox, one receipt,
  one Communication, one action/audit/workflow chain, and four clean losers with no partial facts.
- Shared Manual/Fake/Future dispatcher tests cover exact replay, same-key changed payload, provider
  rejection/retry, malformed provider results, post-acceptance recovery, and no raw recipient or
  rendered content in general audit/workflow evidence.
- Public behavior tests cover success, replay, role/object-scope denials, CFC-only denial, current
  Credit Manager and scoped Senior Finance authority, changed canonical contact/template/rendered
  facts, stale transfer/register/intent/upstream evidence, safe errors, and zero financial writes.
- Dependency and model-owner tests prove only communications owns template/render/delivery/receipt/
  audit policy, the 009H3A receipt table and ids remain exact, and no communications↔disbursements
  executable cycle or second migration is introduced.

## Evidence Required
Failing-first crash-window and template-drift output; matching green runs; sanitized exact replay,
rejection/retry, malformed-result, permission, current-truth, and audit-redaction results; final
focused advice-owner suite; dependency graph; Django check and migration-sync proof; both declared
PostgreSQL five-caller methods in two final independent executions; protected-path and diff-limit
results. Save all evidence in this slice's own run folder.

## Retained Failed-Run Evidence Allocation
- Reproduce `red-outbox-crash-window.txt`, `green-outbox-crash-window-attempt-1.txt`,
  `red-outbox-template-drift.txt`, and `green-outbox-template-drift.txt` as the mandatory TDD cycles.
- Reproduce the final owner/focused gate logs and both `postgresql-final-five-race-run-1.txt` and
  `postgresql-final-five-race-run-2.txt`; intermediate attempt logs remain diagnostic only.
- Consume 009H3A's new schema/row-identity manifest instead of repeating its migration ownership
  implementation; still run migration sync and retained-owner regressions.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
None. Consume the communications-owned outbox and receipt state created by 009H3A. Do not add,
rename, drop, recreate, or alter a second outbox/receipt table or migration.

## Predicted Diff Budget
Target 1,050-1,450 changed lines across the dispatcher/context seam, shallow workflow integration,
public/crash/race tests, and evidence; stop and resplit before implementation if the forecast
exceeds 1,650 lines. The 009H3A schema/adapter foundation keeps this comfortably below 2,000.

## Risk Level
High

## Material Risks
- Duplicate external advice after provider acceptance but before local finalization.
- Changed recipient/template/render/entity facts being reused under one provider key.
- Raw borrower email, rendered financial advice, or bank/UTR content leaking into general audit.
- Concurrent callers retaining partial or multiple Communication/action/audit/workflow facts.
- Role/current-truth regression or accidental mutation of financial and downstream state.
- A future real provider failing to honor the supplied idempotency key; the Future seam must expose
  this residual integration obligation without claiming external sandbox proof.

## Acceptance Criteria
- One stable advice key cannot produce two logical provider messages across tested crash/retry/race
  paths, and changed frozen facts conflict before dispatch.
- Communications alone owns template/render/delivery/receipt/Communication/audit policy behind one
  narrow dispatcher while disbursements supplies immutable context without a dependency cycle.
- Every retained 009H2 authority, secrecy, current-truth, API, and no-financial-side-effect guarantee
  remains exact under focused and twice-run PostgreSQL acceptance.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing crash/template/adapter/ownership tests written first
- [ ] Communications dispatcher and durable outbox finalization implemented
- [ ] Legacy disbursement advice policy removed or made shallow
- [ ] Twice-run PostgreSQL five-caller evidence saved
- [ ] API contracts updated only if the public shape changes
- [ ] Risk assessment, handoff, state, and evidence updated
- [ ] Commit delegated to the orchestrator after gates
