# Failure Summary

- Run: 2026-07-12_171448_normal_run
- Mode: normal_run
- Slice: 006Y9-member-form-real-session-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: slice-specific trusted browser contract is missing or invalid.
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: second trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: one or more declared browser screenshots are missing or empty.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- FAIL: slice-specific trusted browser contract is missing or invalid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- FAIL: second trusted slice-specific browser run did not pass.
- FAIL: one or more declared browser screenshots are missing or empty.

Declared specs:
- sfpcl-lms/e2e/member-governance-variants.e2e.spec.ts
Declared screenshots:
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/006Y9-member-form-real-session-closure.md
docs/working/HANDOFF.md
.ralph/runs/2026-07-12_171448_normal_run/
sfpcl-lms/e2e/member-governance-variants.e2e.spec.ts
```
