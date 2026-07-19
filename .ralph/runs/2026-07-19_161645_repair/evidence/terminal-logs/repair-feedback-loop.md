# Repair Feedback Loop

## Authoritative RED

The normal run's trusted browser command was:

```text
RALPH_EVIDENCE_DIR=.../run-1 E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/epic-009-staff-disbursement-closure.e2e.spec.ts
```

It reached real Django login, current-user, Loan Account list, and Loan Account detail responses, then
failed deterministically at the sanctioned-summary assertion:

```text
strict mode violation: getByText('Sanctioned', { exact: true }) resolved to 2 elements
1) sanctioned status badge
2) sanctioned KPI label
```

Source: the retained full log at
`.ralph/runs/2026-07-19_154507_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log`.

## Repair

The assertion is now scoped to the account-header container identified by the exact Loan Account
number heading. That container contains the status badge but not the KPI label, retaining exact
visible-state proof without changing production markup.

## Local replay limitation

The same exact spec was attempted in the repair sandbox with the repair evidence directory and the
required shared backend interpreter. The web server became ready, but Chromium was terminated at
launch before the first test step:

```text
Error: browserType.launch: Target page, context or browser has been closed
1 failed (4ms)
```

This is the declared macOS browser-sandbox limitation, not a product/spec assertion result. No
screenshots were fabricated. The independent orchestrator must run the trusted contract twice.

## Focused GREEN checks

Playwright collection:

```text
Listing tests:
  [chromium] > epic-009-staff-disbursement-closure.e2e.spec.ts > S36-S41 and initial Loan Account 360 use real Django and retain distinct evidence
Total: 1 test in 1 file
Exit code: 0
```

Focused ESLint:

```text
npx eslint e2e/epic-009-staff-disbursement-closure.e2e.spec.ts
Exit code: 0
```

Boundary scan for `page.route`, `route.fulfill`, auth-storage setters, and init-script injection:

```text
No matches
Exit code: 0
```

Candidate whitespace audit:

```text
git diff --check
Exit code: 0
```
