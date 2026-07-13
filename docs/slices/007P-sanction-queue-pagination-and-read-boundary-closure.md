# Slice 007P: Sanction Queue Pagination and Read-Boundary Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007N

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Preserve authoritative S21 totals/pages through the shared frontend transport and make approval
collection validation work follow safe actor/status/type narrowing instead of a misleading
query-count assertion.

## Source / Review References

- `docs/source/screen-spec.md` S21
- `docs/source/api-contracts.md` §§6.2, 8.1, 25.3, and §44
- `docs/source/codebase-design.md` §§7.2, 23.3-23.5, 26.1-26.3, 27.1, and 36.1
- `docs/slices/007K-frozen-review-snapshot-and-selector-boundary-closure.md`
- `docs/slices/007L-sanction-workbench-contract-and-browser-closure.md`
- `docs/slices/007N-register-matrix-settings-contract-and-browser-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_034706_architecture_review`

## Concrete Requirements

1. `sanctionApi` must use the shared typed paginated request and return rows plus the exact server
   pagination object. S21 displays `total_count`, sends explicit page/page size, exposes existing
   pagination controls, and atomically replaces rows and pagination on filter/page changes.
2. Remove the fixed first-100 truncation. Pending-my-approval still sends
   `approval_type=sanction&current_status=pending&assigned_to_me=true`; historical filters retain
   their exact status and sanction type on every page. Permission loss/error clears rows and totals.
3. The shared client must reject a successful collection envelope whose data is not an array or
   whose required pagination object/fields are absent, malformed, negative, or internally
   inconsistent. It must not fabricate `EMPTY_PAGINATION` for a malformed server response.
4. Apply actor scope plus safe approval type/status/assignment query narrowing before canonical
   Python validation, while still validating every returned/countable case through the frozen
   boundary before count/page serialization. Register-specific filters remain after object scope.
5. Replace exact SQL/query-count tests with observable instrumentation: populate enough
   SQL-candidate and noncandidate cases to cross pages, count canonical validator invocations, and
   prove irrelevant actors/types/statuses are not materialized while malformed stale-true rows do
   not create page holes or leak totals.

## Trusted Browser Acceptance

- Spec: `e2e/sanction-workbench.e2e.spec.ts`
- Screenshot: `sanction-paginated-filtered-queue.png`

## Trusted Browser Scenario

Open the routed S21 workbench in the production app shell with a deterministic multi-page standard
list envelope. Prove the displayed total is larger than the current page, move to the next page,
change status, and assert every request retains sanction/object-scope filters and top-level
pagination. A deliberately malformed list envelope must render the existing error state.

## Test Cases

- Valid, missing, malformed, and inconsistent shared pagination envelopes, plus auth/error parity.
- More than 100 readable cases remain reachable with server total/order and stable page controls.
- Filter/page changes, permission loss, empty and malformed responses replace all prior state.
- Behavioral candidate-work regression uses real validator-call/page outcomes, not SQL text or
  statement count.

## Evidence Required

Frontend/backend RED/GREEN output, validator-work measurements, the trusted screenshot in both
orchestrator runs, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- S21 never truncates or client-counts the authoritative queue.
- Malformed pagination cannot masquerade as an empty successful page.
- Approval read work is observably narrowed without trusting stored projection flags as authority.
