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
