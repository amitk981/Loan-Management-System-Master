# Execution Plan

Selected slice: 012G-critical-e2e-uat-smoke-scenarios

## Repair Boundary

Repair only the trusted-browser failure recorded by
`.ralph/runs/2026-07-25_085034_repair/failure-summary.md`. Preserve the existing candidate and do
not broaden product scope. The authoritative application failure is the UAT-014/015/016/017 DPD
assertion (`principal_overdue_amount` expected `300000.00`, received `400000.00`). Later
pre-page Chrome launch failures are infrastructure diagnostics, not evidence for a product change.

## Permissions Check

- Read `.ralph/permissions.json` before editing.
- Candidate edits are limited to allowed `sfpcl-lms/**`, `sfpcl_credit/**`, and this run's
  `.ralph/runs/2026-07-25_090921_repair/**` evidence.
- Do not edit protected workflow files, `docs/source/**`, orchestrator-owned state/progress,
  selected-slice status, or historical run evidence.

## Feedback Loop and Diagnosis

1. Inspect the existing critical UAT spec, seed command, and the public repayment/DPD contracts
   exercised by the failed step.
2. Reproduce the exact trusted-browser command into current-run terminal evidence when Chromium
   can launch. If launch fails before page creation, retain that infrastructure result and use a
   focused public-contract test/probe that deterministically distinguishes seed expectation drift
   from repayment replay or DPD calculation defects.
3. Rank and test falsifiable hypotheses one at a time. Treat the source-defined principal-first
   allocation and canonical public API result as authoritative; do not weaken an assertion merely
   to match an unexplained value.

## Minimal Repair

4. If the failure is a tracer expectation defect, add or strengthen the nearest focused regression
   around the expected outstanding/overdue principal, capture red evidence, then minimally correct
   the tracer expectation and capture green evidence. If it is production behavior, use backend TDD
   with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and keep the fix inside the demonstrated
   repayment/DPD domain.
5. Do not add new APIs, permissions, business rules, live integrations, styling, or unrelated UAT
   scenarios.

## Focused Validation and Evidence

6. Rerun every focused test affected by the repair. Run frontend typecheck, lint, and build if the
   frontend candidate changes; run Django check/migration consistency only if backend code changes.
7. Rerun the exact trusted browser spec, producing both declared screenshots in the current run.
   Run it twice against fresh deterministic seeds when browser infrastructure permits. Do not
   fabricate screenshots or treat a pre-page launch failure as an application failure.
8. Save the diagnosis, exact commands/output, screenshot evidence, and deterministic result in the
   current run only. Remove any temporary instrumentation.
9. Finish `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review-packet
   Result exactly to `Ready for independent validation`.
