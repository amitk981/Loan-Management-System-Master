# Failure Summary

- Run: 2026-07-12_211948_normal_run
- Mode: normal_run
- Slice: 006Y11-member-form-container-and-error-matrix-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: second trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: one or more declared browser screenshots are missing or empty.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- FAIL: second trusted slice-specific browser run did not pass.
- FAIL: one or more declared browser screenshots are missing or empty.

Declared specs:
- e2e/member-governance-variants.e2e.spec.ts
Declared screenshots:
- member-individual-complete-reloaded.png
- member-institution-complete-reloaded.png
- member-producer-institution-complete-reloaded.png
- member-identity-requester-denied.png
- member-identity-checker-approved.png
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/006Y11-member-form-container-and-error-matrix-closure.md
docs/slices/006Z2-portal-application-limit-display-authority.md
docs/slices/006Z4-active-member-rule-and-snapshot-closure.md
docs/working/HANDOFF.md
docs/working/digests/epic-004-member-kyc-master.md
sfpcl-lms/e2e/member-governance-variants.e2e.spec.ts
sfpcl-lms/src/pages/members/MemberGovernanceForm.tsx
sfpcl-lms/src/pages/members/MemberProfile.container.test.tsx
sfpcl-lms/src/pages/members/MemberProfile.tsx
sfpcl-lms/src/services/memberProfileApi.ts
.ralph/runs/2026-07-12_211948_normal_run/
sfpcl-lms/src/pages/members/MemberGovernanceForm.container.test.tsx
```
