# Execution Plan

Run: 2026-07-24_224117_repair
Selected slice: 011PA-default-case-notes-frontend-wiring
Mode: same-worktree repair

## Demonstrated failure

The exact trusted-browser run launches Chromium and renders the S53-S55 page, then fails because
the spec applies `getByRole('textbox').toHaveCount(0)` to the whole page and observes two controls.
The bounded repair must determine whether those controls are legitimate shell/search inputs or
editable frozen-note fields, then correct only the trusted-browser acceptance domain.

## Permission check

- `.ralph/runs/2026-07-24_224117_repair/**` is allowed for run evidence.
- `sfpcl-lms/src/**` is allowed for frontend product/test changes.
- Protected configuration, workflow scripts, source documents, orchestrator-owned state/progress,
  selected-slice status, and historical run evidence will not be modified.
- The existing candidate and declared E2E spec will be preserved unless the failing assertion is
  proven to mis-scope the slice requirement; no dependency or styling change is planned.

## Repair steps

1. Inspect the rendered control ownership and the declared E2E assertion against the page/component
   tests to identify the two textboxes.
2. Retain the exact Playwright invocation as the red-capable feedback loop and save the preserved
   failing output in this run's evidence.
3. Apply the smallest correction within the demonstrated browser-validation domain, preserving the
   approved visual patterns and the frozen non-payment evidence contract.
4. Rerun the exact declared Playwright spec until it passes, then rerun it a second time with
   isolated screenshot evidence; also run the focused frontend tests, typecheck, lint, and build.
5. Save the browser evidence, risk assessment, review packet, and final summary. Set the review
   packet Result exactly to `Ready for independent validation`.

## Outcome

- The prior application-level failure is addressed by the preserved scoped note-region assertion.
- Focused tests, static trusted-browser contract validation, Playwright discovery, typecheck, lint,
  build, and diff checks pass.
- The coding sandbox's exact run stopped before page creation at system-Chrome launch. No screenshot
  was fabricated; the orchestrator's outside-sandbox two-run validator remains authoritative.
