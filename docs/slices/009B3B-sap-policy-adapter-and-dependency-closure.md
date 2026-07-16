# Slice 009B3B: SAP Policy, Adapter, and Dependency Closure

## Status
Not Started

## Origin
Oversized slice: `009B3`

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009B3A

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Move all executable SAP request, retained-workbook delivery, completion, reuse, read, and adapter
policy behind the canonical `sap_workflow` public owner and remove the Finance↔SAP dependency cycle.

## Source / Review References

- `docs/source/codebase-design.md` §§16.1, 20.1-20.4, 22, 26-28, 36.2, and 42
- `docs/source/integrations.md` §§8.1-8.5 and INT-SAP-001 through INT-SAP-006
- `docs/source/api-contracts.md` §§6-8 and 29
- `docs/source/auth-permissions.md` §§30.1-30.3 and 34.7
- `docs/source/data-model.md` §§19.1-19.2, 28-30, and 34
- `docs/source/functional-spec.md` BR-047 through BR-050 and M07-FR-001 through M07-FR-008
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_143718_architecture_review`
- Failed oversized run `.ralph/runs/2026-07-16_174245_normal_run/`

## Concrete Requirements

1. Move executable request/create/send/complete/reuse/read, delivery-capability, retained Annexure
   storage decisions, and related selectors behind `sap_workflow.modules.sap_customer_profile`,
   consuming only the canonical model state delivered by `009B3A`.
2. No executable `sap_workflow` file may import `finance.models`, `finance.modules`, or private
   Finance storage/policy helpers. Remove the bidirectional Finance↔SAP edge; Finance route shells
   and loans/disbursements may consume only the public SAP interface.
3. Keep the Manual/Fake/Future `SapAdapter` contract inside the SAP owner. `sent` still requires
   exact checksum-verified workbook acceptance and frozen-assignee capability; completion/reuse
   remains supplied/omitted-exact; no real SAP/email service is introduced.
4. Preserve the exact public 009B2 routes, response fields, status codes, idempotency identities,
   secrecy, ciphertext-at-rest behavior, audit vocabulary/context, workflow/task relations, and
   zero-side-effect denials. Align touched conflicts and stale-state responses with source §7 while
   retaining actionable field details and one error taxonomy.
5. Delete or reduce legacy Finance orchestration to policy-free public forwarding only. Any
   temporary legacy import must be one-way, explicitly tested, and contain no model query, action,
   adapter, capability, workbook-storage, or decision implementation.

## Test Cases

- Dependency-graph tests parse imports across `sap_workflow`, `finance`, `loans`, and
  `disbursements`, reject executable SAP→Finance edges and cycles, and exercise behavior only
  through the public SAP interface rather than source-substring proxies.
- Public create/send/download/complete/reuse/read tests retain exact 009B2 success, denial,
  idempotency, replay, stale-state, audit, ciphertext, and zero-write behavior after the move.
- Manual and Fake adapters pass one shared contract suite; the Future seam stays replaceable and
  cannot bypass workbook acceptance, frozen assignment, or exact supplied/omitted replay.
- Twice-run PostgreSQL request/code races retain one winner and zero loser success artifacts after
  the policy move; delivery/read capability races disclose neither file identity nor token material.
- Downstream selector tests prove loans and disbursements receive the immutable SAP decision without
  importing Finance internals or changing account/readiness/payment truth.

## Evidence Required

Failing-first dependency probe; final import graph; sanitized public and denied flows; adapter
contract; route compatibility; focused tests; twice-run PostgreSQL races; full configured gates.

## Risk Level
High

## Acceptance Criteria

- `sap_workflow` owns SAP executable behavior and adapters without private Finance imports.
- Existing API, audit, secrecy, idempotency, and concurrency guarantees remain exact.
- Epic 009 downstream code depends on one deep replaceable SAP seam with no dependency cycle.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Policy and adapters moved to SAP owner
- [ ] API contracts preserved
- [ ] Database/concurrency rules preserved
- [ ] Permissions and denials tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
