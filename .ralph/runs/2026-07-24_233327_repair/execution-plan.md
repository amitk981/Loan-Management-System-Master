# Execution Plan

Selected slice: 011PB-recovery-decision-frontend-wiring

Mode: same-worktree repair

## Demonstrated failure domain

The authoritative trusted-browser run launched Chromium, opened S56, and failed on the exact
Playwright assertion at `default-closure-compliance-staff.e2e.spec.ts:68`. The unscoped
`getByText('Browser Committee Approver')` locator matches the approver in both required-approver
evidence and recorded approval-action evidence, so Playwright strict mode stops before the
decision mutation and screenshot.

## Bounded repair

1. Reproduce the strict-locator failure with the exact declared trusted-browser spec and save the
   current repair-run log.
2. Change only the ambiguous acceptance locator(s), preserving the product candidate and asserting
   the intended repeated approval-evidence rendering explicitly.
3. Rerun the exact declared trusted-browser command twice, each with its own screenshot directory,
   and verify `recovery-approval-decision.png` is a valid non-empty PNG in both runs.
4. Run the focused E2E spec-list check and the relevant frontend test/typecheck/lint/build gates if
   the repair changes anything beyond the browser assertion.
5. Save browser evidence, risk assessment, review packet, and final summary. Set the review packet
   Result to exactly `Ready for independent validation`.

## Permissions and scope

`.ralph/permissions.json` permits edits under `sfpcl-lms/src/**` and `.ralph/runs/**`; the E2E spec
is under the permitted frontend tree. No protected or forbidden path will be changed. The repair
will not modify product code unless the exact browser rerun reveals a same-validator product error
after the locator is corrected.

## Outcome

- Exact strict-locator root cause confirmed against the rendered component structure.
- Both affected approver assertions corrected without a product-code change.
- Focused tests, Playwright discovery, typecheck, lint, build, static browser contract, and diff
  whitespace validation passed.
- The exact browser retry was blocked before the test body by the coding sandbox's system-Chrome
  boundary. The required two passing screenshot runs remain for independent trusted validation.
