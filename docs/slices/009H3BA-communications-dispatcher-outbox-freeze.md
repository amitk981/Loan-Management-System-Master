# Slice 009H3BA: Communications Dispatcher and Outbox Freeze

## Status
Not Started

## Origin
Oversized slice: `009H3B`

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Depends On
- 009H3A

## Goal
Establish the one-way communications dispatcher/context seam and close every pre-provider
template, payload, and crash-retry hazard by freezing the complete canonical advice in the 009H3A
outbox before adapter dispatch.

## Vertical Boundary
This slice moves approved/effective template resolution, exact variable and sensitive-value
validation, rendering, outbox freeze, provider dispatch, and provider-result validation into
`communications.modules.communication_dispatcher`. Disbursements continues to own authority,
locked financial context, and the existing local final-ledger transaction until 009H3BB moves that
finalization behind communications. The intermediate state must be fully green: there is one owner
for template/render/dispatch policy, exact public behavior remains intact, and no duplicate external
message can be emitted after an accepted-provider crash.

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/api-contracts.md` §§31.5, 39, and 45
- `docs/source/integrations.md` §§9-10, 19.3, and 21
- `docs/source/codebase-design.md` §§20.6, 22.2, 26.3, 36.2, 40.1-40.2, and 42.4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`
- Retained oversized run `.ralph/runs/2026-07-18_022416_normal_run/`

## Concrete Requirements
1. Create `communications.modules.communication_dispatcher` as the single executable owner of
   approved/effective template resolution, exact declared-variable and sensitive-value validation,
   rendering, the durable outbox/provider boundary, adapter dispatch, and provider-result
   validation. Remove those policies from `disbursements.modules.disbursement_advice`; do not leave
   a second template, rendering, outbox, or dispatch implementation.
2. Keep disbursements as the owner of advice intent, authority, and immutable upstream financial
   context. Supply only a frozen primitive/context contract to communications. Communications must
   not import disbursement models/modules, query financial policy, or save disbursement-owned action
   state. Preserve a one-way composition seam that 009H3BB can finish without changing the public
   route.
3. Before any provider call, durably freeze and commit the stable advice intent/idempotency key,
   communication identity, canonical recipient and digest, approved template identity/name/type/
   language/audience/version/approval/effective-range/declared variables/source templates/checksum,
   rendered subject and body, canonical payload digest, and related entity in the existing 009H3A
   outbox. Do not add or alter a model or migration.
4. Reconcile every exact retry against the frozen outbox before dispatch. The same key with changed
   email/recipient, template provenance, subject, body, payload, or related entity is a safe conflict
   before another provider invocation, including after a local crash and with a fresh adapter.
   Exact retry must reuse one logical provider identity.
5. Complete the Manual/Fake/Future dispatcher contract for exact replay, stable provider identity,
   provider rejection and retry, and malformed results. Rejection leaves the outbox pending and
   retryable. Malformed results fail closed without sent, receipt, Communication, or disbursement-
   owned success truth. Once acceptance is recorded in the outbox, a retry resumes from that result
   without invoking a second logical external message.
6. Preserve every 009H2 role/object-scope rule and current canonical contact, template, transfer,
   register, advice-intent, and upstream reconciliation through the disbursement-owned context.
   Preserve recipient masking, safe errors, exact replay shape, and zero changes to financial or
   downstream state.
7. Preserve `POST /api/v1/disbursements/{id}/send-advice/` request/response/status behavior. Do not
   change money, transfer, loan-account, register, checklist, repayment, schedule, interest,
   default, closure, or borrower-portal truth. The local final-ledger ownership retained for this
   bounded intermediate slice must be removed by 009H3BB, not expanded here.

## Test Cases
- Failing-first ownership test proves the dispatcher initially does not exist or policy remains in
  disbursements; green proof requires the communications module, no executable communications-to-
  disbursements import, no direct save of supplied disbursement objects, and no duplicate template/
  render/dispatch functions in the legacy module.
- Simulate provider acceptance followed by failure before receipt update. Prove the outbox was
  committed first and retains the accepted provider tuple; a fresh-adapter exact retry uses the same
  provider identity, while changed payload, recipient/email, subject/body, or entity conflicts
  before a second invocation or changed final evidence.
- Failing-first template-drift coverage changes each frozen provenance dimension, including
  language, audience, effective range, declared variables, and source templates. Each change must
  conflict before redispatch; an exact template retry remains green.
- Shared Manual/Fake/Future dispatcher tests cover exact replay, same-key changed payload,
  rejection/retry, malformed provider results, accepted-result recovery, and stable identity across
  changed payload and fresh adapter instances.
- Retained public smoke tests cover success/replay, relevant role and object scope, current contact/
  template/upstream drift, safe errors, and zero financial writes so this transitional slice is
  independently green.
- Static owner/migration tests prove communications owns the new policy without an executable cycle,
  the 009H3A receipt/outbox tables and ids remain exact, and no second migration is introduced.

## Evidence Required
- Reproduce `red-communications-owner.txt` and `green-communications-owner.txt`.
- Reproduce `red-outbox-crash-window.txt` and `green-outbox-crash-window-attempt-1.txt`.
- Reproduce `red-outbox-template-drift.txt` and `green-outbox-template-drift.txt`.
- Save sanitized Manual/Fake/Future exact-replay, changed-payload, rejection/retry, malformed-result,
  and accepted-result recovery output; focused dispatcher/public smoke output; the one-way dependency
  graph; Django check; migration sync; protected-path results; and the slice diff-limit result.
- Consume 009H3A's schema/row-identity manifest rather than repeating migration ownership work.
  Intermediate diagnostic logs do not replace the named final green evidence.

## Retained Failed-Run Allocation
This slice owns the failed candidate's `communication_dispatcher` foundation, frozen disbursement
context input, pre-provider outbox commit, template checksum/provenance binding, adapter-result
validation, and the three mandatory RED/GREEN cycles above. 009H3BB owns final receipt/
Communication/audit/workflow retention, the second final-Communication crash window, the complete
public matrix, and both final PostgreSQL race executions.

## Runtime Capabilities

none

## Database / Migration Impact
None. Consume the communications-owned outbox and receipt state created by 009H3A. Do not add,
rename, drop, recreate, or alter an outbox/receipt table or migration.

## Predicted Diff Budget
Target 850-1,150 changed lines across the dispatcher, context seam, focused tests, and evidence.
Stop and request another oversized-slice rewrite before implementation if the forecast exceeds
1,350 lines. This is comfortably below the configured 2,000-line limit.

## Risk Level
High

## Material Risks
- Duplicate external advice after provider acceptance but before local receipt finalization.
- Changed recipient/template/render/entity facts being reused under one stable provider key.
- A communications-to-disbursements dependency cycle or direct save of financial owner state.
- Provider rejection or malformed results fabricating accepted local truth.
- Role/current-contact/upstream regression or accidental mutation of financial/downstream state.
- A future real provider failing to honor the supplied idempotency key; the Future seam must expose
  this residual integration obligation without claiming external sandbox proof.

## Acceptance Criteria
- Every provider-relevant fact is frozen in the durable 009H3A outbox before dispatch; one stable
  key cannot produce two logical provider messages across tested crash/retry/drift paths.
- Communications alone owns template resolution, validation, rendering, outbox, adapter, and
  provider-result policy behind a one-way context interface, while disbursements still owns
  authority/current financial facts and saves no such policy.
- Existing public success/replay/authority/current-truth/secrecy/no-financial-side-effect behavior
  remains green in the independently shippable intermediate state.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing ownership/crash/template/adapter tests written first
- [ ] Dispatcher/context seam and pre-provider outbox freeze implemented
- [ ] Manual/Fake/Future adapter and accepted-result recovery contract green
- [ ] Legacy template/render/dispatch policy removed
- [ ] Focused public/owner, dependency, Django, migration, and diff evidence saved
- [ ] Risk assessment, handoff, state, and evidence updated
- [ ] Commit delegated to the orchestrator after gates
