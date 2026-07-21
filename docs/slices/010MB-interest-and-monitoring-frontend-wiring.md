# Slice 010MB: Interest and Monitoring Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `010M`

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Complete oversized 010M by wiring Interest Management (S47-S49) and the Monitoring Dashboard's DPD
and reminder workflows (S50-S52) after the shared servicing transport foundation lands in 010MA.

## User Value
Permitted finance staff can inspect and trigger canonical interest operations, while Credit and CFO
roles can monitor overdue loans and retained reminder work without mock or browser-derived policy.

## Depends On
- 010MA

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/servicing-monitoring-workflows.e2e.spec.ts`
- Screenshot: `interest-management.png`
- Screenshot: `monitoring-dashboard.png`

## Source References
- docs/source/screen-spec.md screens S47-S52 and section 9.8 (interest rules)
- docs/source/api-contracts.md sections 33 (interest), 34 (monitoring/reminders), and 45
  (idempotency contract)
- docs/source/functional-spec.md BR rules for 30-April capitalisation
- docs/source/test-plan.md (financial calculation test expectations)
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` shared invariants and
  §010M–010O

## Prototype Reference
- sfpcl-lms/src/pages/interest/InterestManagement.tsx
- sfpcl-lms/src/pages/monitoring/MonitoringDashboard.tsx

## Concrete Requirements
1. Extend the canonical servicing transport seam established by 010MA for interest, DPD, and
   reminder endpoints using standard envelopes/errors. Display backend Money, calculation, DPD,
   delivery, and permission projections; do not aggregate buckets or derive financial/state policy
   in the browser.
2. Wire `InterestManagement.tsx` to invoice list/generation state (010F), accrual run/status (010G),
   and capitalisation preview/result (010H). Each trigger uses one caller-stable idempotency key,
   appears only for the exact permitted role, and preserves backend 403/validation/error truth
   without optimistic financial state.
3. Wire `MonitoringDashboard.tsx` to canonical DPD bucket/row projections (010I) and retained
   reminder eligibility, delivery, and follow-up rows (010J) using the existing KPI/queue patterns.
   Add only the scoped canonical reminder read projection needed by S52 if absent; do not synthesize
   reminder rows from age/policy in the frontend.
4. Treat any failed per-loan DPD or reminder read as a visible error rather than silently presenting
   a partial successful aggregate. Exclude reminder recipient/message content and preserve canonical
   staff loan-object scope.
5. Use the existing prototype components and patterns without new styling. Supply loading, empty,
   error, unauthorised, validation, and success states for every owned read/mutation surface.

## Owned Mock Removals
This terminal successor inherits 010M's final-removal ownership for:
- `src/pages/monitoring/MonitoringDashboard.tsx`

After it, the file may not import `src/data/mockData.ts`, keep inline production business fixtures,
classify DPD locally, or derive reminder eligibility locally. `InterestManagement.tsx` must also be
fully backend-wired and fixture-free within this slice's declared surface.

## Test Cases
- Invoice, accrual, preview, and capitalisation values/states render from backend projections; each
  permitted trigger sends one stable idempotency key and refreshes canonical truth.
- A non-permitted role cannot trigger accrual/capitalisation in the frontend, and a backend 403 is
  retained as an unauthorised state without optimistic mutation.
- DPD bucket counts/rows and reminder queue entries exactly match seeded backend fixtures, including
  retained delivery/follow-up evidence; no client bucket aggregation or policy-derived rows occur.
- Loading, empty, validation, read failure, and unauthorised states are visible; one failed DPD or
  reminder request cannot be hidden behind a partial dashboard.
- The owned monitoring file has no mock import, inline production fixture, local DPD classification,
  or reminder policy.

## Out of Scope
Account/repayment/reconciliation wiring (010MA), member portal loan views (010L done), CFO quarterly
MIS backend (010K), default workflows (011x), and global search (010N).

## Evidence Required
Saved RED/GREEN interest/monitoring service and component results; exact envelope, Money,
permission, idempotency, 403, validation/error, DPD/reminder fidelity, partial-failure, and mock-
removal evidence; backend RED/GREEN evidence for any scoped reminder read projection; focused
reverse-consumer and configured frontend/backend gates; and both trusted-browser screenshots from
two passing contract runs using real backend login/current-user authority without an auth mock.

## Retained Failed-Run Evidence Allocation
- Retained run `.ralph/runs/2026-07-21_102540_normal_run/` is a requirements map only; failed-
  candidate code is not acceptance evidence and this successor must recreate every assigned proof.
- Reproduce the interest/monitoring portions of `servicing-api-red.log`, `servicing-api-green.log`,
  `servicing-workspaces-red.log`, `servicing-workspaces-green.log`, and the final focused frontend
  result. Recreate the reminder portion of `backend-read-projections-red.log`/`green.log` and the
  reminder-queue impacted tests when backend support is needed.
- Recreate the `interest-management.png` and `monitoring-dashboard.png` assertions from the retained
  four-scenario Playwright collection. Re-run typecheck, lint, build, mock/auth static audits, and
  all risk-selected gates in this successor's own run folder.

## Predicted Diff Budget
Target 700-1,050 changed lines across transport extensions, two production surfaces, any narrow
reminder read projection, focused tests, documentation, and the two-scenario browser contract. Stop
and resplit before implementation if the forecast exceeds 1,350 lines. This is comfortably below
the configured 2,000-line limit because 010MA owns the shared foundation and account/repayment work.

## Risk Level
High

## Material Risks
- Client-derived invoice, accrual, capitalisation, DPD, or reminder policy diverging from backend
  financial and monitoring truth.
- Duplicate interest mutations after replay or optimistic UI state that claims an uncommitted run.
- CFO/Auditor read access being confused with mutation authority, or 401/403/404 scope being hidden.
- Partial DPD/reminder failures producing deceptively complete KPI totals or policy-derived rows.
- Reminder message/recipient content or another loan/member's retained evidence being exposed.

## Acceptance Criteria
- S47-S52 interest and monitoring surfaces run on canonical backend data, including exact DPD buckets
  and retained reminder delivery/follow-up evidence.
- Interest trigger visibility, backend 403, stable-key replay, validation, and error behavior are
  proved with no client-owned money, DPD, reminder, or permission decisions.
- The terminal inherited mock-removal owner is clean; configured gates and both twice-run browser
  screenshot contracts pass independently.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing service/component and any backend read-projection tests written first
- [ ] Interest and DPD/reminder monitoring wiring implemented
- [ ] API contracts updated if a scoped reminder read projection is added
- [ ] Permissions, idempotency, replay, validation, partial-failure, and mock removal tested
- [ ] Trusted browser evidence saved from two passing runs
- [ ] Tests/typecheck/lint/build and all risk-selected gates passed
- [ ] Risk assessment and review packet completed
- [ ] Commit delegated to the orchestrator after gates
