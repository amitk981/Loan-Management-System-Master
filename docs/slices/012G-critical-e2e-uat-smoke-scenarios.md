# Slice 012G: Critical E2E UAT Smoke Scenarios

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Automate a bounded cross-module tracer suite that proves the critical UAT journeys, negative
permission/security path, financial state, and audit evidence through public UI/API boundaries.

## User Value
Business UAT starts with repeatable evidence that the platform's highest-risk end-to-end journeys
work together, instead of discovering integration failures manually at signoff time.

## Depends On
- 012F2
- 011P
- 012DA
- 012EB

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/critical-uat-smoke.e2e.spec.ts`
- Screenshot: `critical-uat-standard-loan.png`
- Screenshot: `critical-uat-permission-negative.png`

## Source References
- `docs/source/test-plan.md` sections 16, 18-22, 27.1-27.2, 28, and 29.4
- `docs/source/implementation-roadmap.md` sections 17.4-17.6 and 27.3
- `docs/source/product-requirements.md` sections 11-12 and 19.2
- `docs/source/screen-spec.md` section 13
- `docs/source/technical-architecture.md` section 29.4
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` section 012G

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
Existing critical workflow screens only: application/eligibility/appraisal/approval,
documentation/security/disbursement, servicing/default/closure/compliance, S69 reports, and S74
audit. No new visual design.

## Frontend Scope
Add only test fixtures/selectors needed to exercise existing UI routes. Use stable accessible
labels/test contracts and public actions; do not alter product UI merely to make automation pass.

## Backend/API Scope
No new business capability. Add deterministic seed/builders and public-API assertions required by
the cross-module scenarios, reusing existing adapters/fakes instead of live providers.

## Database/Model Impact
None.

## API Contracts
None. A contract gap discovered by a scenario is a visible defect/corrective slice, not an
invented test-only endpoint.

## Permissions
Each journey uses the actual source role at every step. Include one explicit RBAC/object-scope and
sensitive masking negative journey; no admin shortcut or direct database state transition.

## Audit Requirements
Assert the existing critical audit events and actor/outcome/reason fields at major state changes;
do not insert audit fixtures as a substitute for running the action.

## Validation Rules
- Cover the smallest tracer set that maps all `UAT-001..026`, allowing one scenario to satisfy
  multiple scripts when the evidence matrix is explicit.
- Minimum journeys: standard loan through disbursement; threshold/exception approval; direct and
  subsidiary repayment plus interest/DPD; default/recovery/closure; compliance; reports/export/
  audit; and permission/masking negative path.
- Assert canonical state, financial ledger/allocation where applicable, documents/evidence,
  permission denial, and audit—not merely HTTP status or visible text.
- Tests are seed-deterministic, isolated, retry-safe, and never depend on execution order or live
  SAP/bank/email/SMS/storage providers.

## Test Cases
- Map each automated scenario to the source UAT and E2E IDs, role, preconditions, public steps,
  expected records/ledger/audit, and retained evidence.
- Boundary variants include below/at/above approval threshold, invalid exception authority,
  duplicate payment/allocation prevention, recovery without approval, premature closure, report
  filter reconciliation, unauthorized export, and audit mutation denial.
- Run the suite twice against fresh deterministic seeds; results/counts must agree and no state may
  leak between scenarios.
- Reverse-consumer regression includes full backend/frontend suites and the 012F security lane so
  test support cannot weaken production permissions or settings.

## Visual Acceptance Criteria
None.

## Evidence Required
Scenario-to-UAT/E2E/source matrix; seed manifest; exact test counts/skips/runtime; key state/ledger/
audit assertions; screenshots/traces for UI scenarios; two-run determinism evidence; full gates.

## Non-Goals
New product features, test-only production APIs, direct database state shortcuts, live provider
calls, broad defect repair, hosting/deployment work, or owner/business signoff.

## Risk Level
Medium

## Acceptance Criteria
- The bounded tracer suite maps every `UAT-001..026` to automated evidence or an explicit manual
  UAT step and covers all minimum critical journeys above.
- Scenarios verify business/financial/audit outcomes and permission negatives through public
  interfaces with deterministic, repeatable results.
- No test-only production endpoint, permission bypass, direct state shortcut, live-provider call,
  broad defect repair, hosting work, or owner signoff is included.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
