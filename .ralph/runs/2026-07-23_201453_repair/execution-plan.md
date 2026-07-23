# Execution Plan

Selected slice: 011NA-member-portal-notices-grievances-and-notifications

## Repair boundary

- Preserve the existing 011NA candidate.
- Repair only the trusted-browser acceptance failure recorded in
  `.ralph/runs/2026-07-23_192235_normal_run/failure-summary.md`.
- Do not change backend/business behavior unless the exact browser reproducer demonstrates that it
  is the cause.

## Permission check

- No product-code edit is planned.
- Repair evidence and review artifacts are permitted under
  `.ralph/runs/2026-07-23_201453_repair/**`.
- The selected slice explicitly owns `sfpcl-lms/e2e/member-portal-communications.e2e.spec.ts` as
  its trusted-browser acceptance spec. It is neither protected nor forbidden, and the quarantined
  candidate already contains it; a bounded assertion correction there preserves the candidate.
- Do not modify protected or forbidden paths.

## Feedback loop and repair steps

1. Reproduce the exact missing closure/NOC status with the declared Playwright spec and retain the
   red output in this repair run.
2. Inspect only the closure page, its portal API projection, and the declared E2E assertion to rank
   and test bounded hypotheses for why the issued status is absent.
3. Correct only the two acceptance assertions that disagree with the existing `StatusBadge`
   borrower-facing title-case rendering; do not change product rendering.
4. Rerun the exact declared Playwright spec until it passes, then rerun it a second time with the
   required mobile screenshot and manifests saved under this repair run.
5. Run the impacted frontend test, typecheck, lint, and build commands; save concise terminal logs.
6. Update `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review result
   exactly to `Ready for independent validation`.
