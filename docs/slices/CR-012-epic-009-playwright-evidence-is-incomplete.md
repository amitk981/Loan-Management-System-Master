# Slice CR-012: Complete and verify the missing Epic 009 Playwright evidence

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Depends On
- 009L
- 009L4

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`
- Screenshot: `loan-account-list.png`
- Screenshot: `loan-account-sanctioned-summary.png`
- Screenshot: `loan-account-active-summary.png`
- Screenshot: `sap-request-and-confirmation.png`
- Screenshot: `disbursement-readiness-blockers.png`
- Screenshot: `payment-initiation.png`
- Screenshot: `cfc-authorisation.png`
- Screenshot: `transfer-and-advice-success.png`
- Screenshot: `loan-account-safe-error.png`

## Fixture and Scope Boundaries
- Provision deterministic Epic 009 Loan Account, SAP, readiness, initiation, CFC, transfer, and
  advice states only through an isolated backend E2E seed guarded by both `SFPCL_DEBUG=true` and
  `SFPCL_ALLOW_E2E_SEED=true`, or through the real production APIs. The seed must refuse without
  either guard and must be idempotent.
- Log in through the real staff login form as the required Credit Manager, Senior Manager Finance,
  and CFC actors. Do not inject authentication tokens into browser storage.
- Do not intercept or fulfil `/api/v1/auth/**`, `/api/v1/loan-accounts/**`,
  `/api/v1/disbursement-workspaces/**`, or their mutation/action URLs with Playwright routing.
  External SAP or bank fakes, if required, stay behind application adapter seams.
- No production API shape, money/workflow rule, permission, styling, or layout change belongs in
  this evidence correction. If real-boundary execution reveals a product defect, fail closed and
  record it separately instead of weakening the proof.

## State and Hash Proofs
- Immediately before each capture, assert the exact visible evidence for that state: Loan Account
  list heading and row; sanctioned badge and zero disbursed; active badge and funded amount; SAP
  request/confirmation status or action; named readiness blocker with initiation unavailable;
  initiation form/action; CFC authorisation action under the CFC login; transfer success plus advice
  state/action; and a safe error produced by a genuine Django 4xx/5xx response.
- Within each trusted run independently, compute SHA-256 for the nine declared basenames and assert
  that there are exactly nine different hashes. Retain a deterministic filename-to-hash manifest.
  The same basename may have the same hash across run 1 and run 2; deterministic repetition is
  valid and must not be rejected.

## Origin
Change request (maintenance stage), accepted 2026-07-19 from docs/change-requests/accepted/CR-012-epic-009-playwright-evidence-is-incomplete.md.

## Risk Level
High

## Change Request (verbatim)

# Complete and verify the missing Epic 009 Playwright evidence

## Type
bug-cross-stack

## Severity
High

## What Is Happening
Epic 009 is marked complete even though its retained Playwright evidence does not fully prove the
visual states promised by slices 009J and 009K. Slice 009J required separate Loan Account list,
sanctioned-summary, active-summary, and safe-error screenshots, but no account-list screenshot was
retained. In both retained 009L runs, `sap-request-and-confirmation.png`,
`disbursement-readiness-blockers.png`, and `payment-initiation.png` are byte-identical, so their
filenames do not prove distinct UI states. The 009L Playwright spec also fulfils the staff API
routes inside the browser instead of exercising the real Django endpoints required by the original
evidence contracts.

## Expected Behaviour
The Epic 009 staff workflow must have one independently captured screenshot for every declared
009J and 009K state. Each screenshot must follow an assertion proving the intended state is visible,
all state screenshots must be content-distinct, and the workflow must use authenticated real Django
responses rather than browser-level interception of the owned staff APIs. Ralph's trusted browser
gate must execute the exact contract twice and retain valid PNG evidence.

## Steps To Reproduce
1. Inspect `docs/slices/009J-loan-account-360-initial-view.md` and note that it requires account
   list, sanctioned summary, active/funded summary, and safe-error screenshots.
2. Inspect `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`; the test clicks
   `LN-E2E-009` before its first Loan Account screenshot, so no list screenshot is taken.
3. List the tracked Epic 009 PNG files under the retained 009L normal and repair run evidence; no
   Loan Account list PNG exists.
4. Hash `sap-request-and-confirmation.png`, `disbursement-readiness-blockers.png`, and
   `payment-initiation.png` in either retained 009L run and observe that all three hashes match.
5. Inspect the Playwright spec and observe browser-level route fulfilment for the authentication,
   disbursement-workspace, and loan-account APIs instead of real Django responses.

## Where It Appears
The Epic 009 trusted Playwright contract and retained evidence for the Loan Account 360, SAP and
Disbursement, and Payment Authorisation staff screens; specifically
`sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts` and the 009L Ralph run evidence.

## Source Document Reference
`docs/source/screen-spec.md` S36-S42; `docs/slices/009J-loan-account-360-initial-view.md` Visual
Acceptance Criteria; `docs/slices/009K-disbursement-and-cfc-frontend-wiring.md` Acceptance Criteria;
and `docs/slices/009L-epic-009-staff-workflow-and-sap-posting-closure.md` Trusted Browser Acceptance.

## Acceptance Criteria
- A real-Django Playwright flow retains separate valid PNGs for the Loan Account list, sanctioned
  summary, active/funded summary, safe error, SAP request/confirmation, readiness blockers, payment
  initiation, CFC authorisation, and transfer/advice success states.
- Every capture is immediately preceded by a state-specific visible assertion that would fail if
  the page remained on the previous state.
- The owned authentication, loan-account, and disbursement-workspace APIs are not fulfilled through
  `page.route()` or another browser-level response stub; any unavoidable external-system fake stays
  behind the application's adapter boundary and is identified in the evidence.
- The screenshot contract fails when any two state screenshots are byte-identical, and retained
  evidence includes a deterministic filename-to-SHA-256 manifest.
- Ralph's trusted browser gate runs the declared spec twice, and both runs produce all declared
  structurally valid screenshots without stale files satisfying the second run.
- Existing 009I2 MP14 Playwright evidence remains valid and all focused frontend/backend, typecheck,
  lint, build, and configured regression gates pass.
- No product styling, business rule, permission, money, or workflow behavior is weakened merely to
  make the evidence pass.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.
