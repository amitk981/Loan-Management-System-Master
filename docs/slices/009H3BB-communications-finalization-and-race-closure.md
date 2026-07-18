# Slice 009H3BB: Communications Finalization and Race Closure

## Status
Not Started

## Origin
Oversized slice: `009H3B`

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Depends On
- 009H3BA

## Goal
Finish the communications owner by making accepted advice finalization crash-safe and atomic, then
prove the complete retained public contract and twice-run PostgreSQL five-caller race.

## Vertical Boundary
Consume 009H3BA's frozen outbox/provider result and move receipt, protected Communication,
delivery-status, communication-audit, and replay/finalization policy behind the dispatcher.
Disbursements supplies locked current context and consumes one immutable ordinary delivery decision
to retain its own action. The resulting terminal slice removes the transitional local finalization
policy and becomes the dependency for all downstream 009H3B consumers.

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/api-contracts.md` §§31.5, 39, and 45
- `docs/source/integrations.md` §§9-10, 19.3, and 21
- `docs/source/codebase-design.md` §§20.6, 22.2, 26.3, 36.2, 40.1-40.2, and 42.4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`
- Retained oversized run `.ralph/runs/2026-07-18_022416_normal_run/`

## Concrete Requirements
1. Make `communications.modules.communication_dispatcher` the single executable owner of the
   complete advice lifecycle: 009H3BA template/render/outbox/adapter policy plus protected
   Communication creation, communications-owned receipt, provider/delivery status, safe
   communication audit/workflow evidence, finalization, and replay reconciliation. Remove or reduce
   `disbursements.modules.disbursement_advice` to a policy-free compatibility boundary; leave no
   duplicate receipt, Communication, delivery, audit, or finalization policy.
2. Preserve disbursements ownership of intent, authority, locked current upstream financial
   context, and its own immutable disbursement action. Communications must not import disbursement
   code or query financial policy. It returns an immutable ordinary `AdviceDeliveryDecision`; the
   context owner consumes that decision under the same transaction without communications directly
   saving supplied disbursement objects.
3. Reconcile the locked current disbursement context against the complete 009H3BA frozen outbox
   before finalization. Changed email, template provenance, subject, body, recipient, payload,
   related entity, provider tuple, transfer/register/intent, or other canonical upstream fact is a
   zero-write conflict and cannot bless historical acceptance.
4. Recover independently from provider acceptance followed by failure before receipt retention and
   failure before final protected Communication commit. A fresh-adapter exact retry must consume the
   retained accepted provider result without a second logical message and finalize exactly once.
   Changed retries must conflict before changed dispatch or final evidence.
5. Atomically retain exactly one communications-owned delivery receipt, one protected
   Communication, one disbursement-owned action, one safe communication audit, and one workflow
   event, all linked to the singular frozen outbox/provider identity. Record every tested adapter
   result; concurrent losers remain clean and cannot retain a partial receipt, Communication,
   action, audit, workflow, or sent outbox state.
6. Preserve every 009H2 role/scope rule, including CFC-only denial, current Credit Manager authority,
   scoped Senior Manager Finance authority, canonical contact/template/upstream reconciliation,
   exact replay, masking, safe response/error contracts, and zero financial/downstream writes.
   General audit/workflow evidence contains only masked/digested recipient and content/provider
   facts—never raw email, rendered subject/body, full UTR, or sensitive bank content.
7. Preserve `POST /api/v1/disbursements/{id}/send-advice/` request/response/status behavior unless a
   source-required correction is unavoidable. Do not change money, transfer, loan-account,
   register, checklist, repayment, schedule, interest, default, closure, or borrower-portal truth.

## Test Cases
- Failing-first finalization tests separately inject failure before receipt retention and before the
  final Communication commit after accepted provider truth exists. Exact fresh-adapter retry retains
  the one provider identity and one complete final chain; changed payload/recipient/template/
  subject/body/entity/provider/upstream facts produce safe zero-write conflicts.
- Five concurrent PostgreSQL callers run in two independently declared test methods. Each method
  records every adapter result and asserts one external provider identity, one frozen outbox, one
  receipt, one protected Communication, one disbursement action, one safe audit/workflow chain, and
  four clean losers. Execute both methods in two separate final runs.
- Shared Manual/Fake/Future final-dispatch tests retain 009H3BA exact replay, changed-payload,
  rejection/retry, and malformed-result coverage, then add post-acceptance recovery and proof that
  no raw recipient, rendered content, full UTR, or sensitive bank facts enter general audit/workflow
  evidence.
- Public behavior tests cover success, replay, role/object-scope denials, CFC-only denial, current
  Credit Manager and scoped Senior Finance authority, changed canonical contact/template/rendered
  facts, stale transfer/register/intent/upstream evidence, safe errors, and zero financial writes.
- Dependency/model-owner tests prove only communications owns template/render/delivery/receipt/
  Communication/audit/finalization policy, the 009H3A receipt table and ids remain exact, no
  communications↔disbursements executable cycle exists, and no second migration is introduced.

## Evidence Required
- Save failing-first and matching green outputs for the before-receipt and before-final-
  Communication crash windows; retain the 009H3BA named outbox/template RED/GREEN evidence as
  prerequisites rather than reproducing its implementation.
- Reproduce `green-advice-owner-suite-final.txt` with the complete focused advice/communications
  owner and public matrix.
- Reproduce `postgresql-final-five-race-run-1.txt` and
  `postgresql-final-five-race-run-2.txt`; each file must run both declared five-caller methods and
  show every-result/one-winner/clean-loser assertions. Intermediate attempts remain diagnostic only.
- Save sanitized exact replay, rejection/retry, malformed result, post-acceptance recovery,
  permission, current-truth, and audit-redaction results; final dependency graph; Django check;
  migration sync; 009H3A retained-owner regressions; protected-path result; and diff-limit result.
- Consume the 009H3A schema/row-identity manifest and 009H3BA outbox contract. Do not repeat either
  migration or pre-provider implementation ownership.

## Retained Failed-Run Allocation
This slice owns the failed candidate's accepted-result finalization, immutable delivery decision,
receipt/Communication/action/audit/workflow chain, policy-free legacy boundary, complete 29-test
owner/public suite, and both final twice-run PostgreSQL logs. Together with 009H3BA, this preserves
every original 009H3B concrete requirement, test, evidence category, and risk.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
None. Consume the communications-owned outbox and receipt state created by 009H3A. Do not add,
rename, drop, recreate, or alter a second outbox/receipt table or migration.

## Predicted Diff Budget
Target 850-1,150 changed lines across finalization/context consumption, legacy-policy removal,
public/crash/race tests, and evidence. Stop and request another oversized-slice rewrite before
implementation if the forecast exceeds 1,350 lines. This is comfortably below the configured
2,000-line limit.

## Risk Level
High

## Material Risks
- Duplicate external advice or duplicate local success after either post-acceptance crash window.
- Changed recipient/template/render/entity/provider/upstream facts blessing historical acceptance.
- Raw borrower email, rendered financial advice, full UTR, or bank content leaking into general
  audit/workflow evidence.
- Concurrent callers retaining partial or multiple receipt/Communication/action/audit/workflow
  facts, or failing to record every adapter result.
- Role/current-truth/API regression or accidental mutation of financial/downstream state.
- Duplicate finalization policy or an executable communications↔disbursements dependency cycle.
- A future real provider failing to honor the supplied idempotency key; preserve the Future seam's
  explicit residual integration obligation without claiming external sandbox proof.

## Acceptance Criteria
- One stable advice key produces one logical provider message and one complete local delivery chain
  across both tested crash windows, exact retries, changed-fact conflicts, and twice-run races.
- Communications alone owns template/render/delivery/receipt/Communication/audit/finalization policy
  behind one narrow dispatcher; disbursements supplies current immutable context and consumes an
  ordinary delivery decision without a dependency cycle.
- Every retained 009H2 authority, secrecy, current-truth, API, exact-replay, and no-financial-side-
  effect guarantee remains exact under the complete focused suite and twice-run PostgreSQL
  acceptance.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing finalization crash tests written first
- [ ] Communications-owned receipt/Communication/audit/finalization implemented
- [ ] Immutable delivery decision consumed by the disbursement context owner
- [ ] Legacy disbursement advice policy removed or made shallow
- [ ] Full public/owner/redaction/current-truth suite green
- [ ] Twice-run PostgreSQL five-caller evidence saved
- [ ] Django, migration, dependency, protected-path, and diff evidence saved
- [ ] API contracts updated only if the public shape changes
- [ ] Risk assessment, handoff, state, and evidence updated
- [ ] Commit delegated to the orchestrator after gates
