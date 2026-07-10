# Review Packet: 2026-07-10_005716_architecture_review

## Result
Success

## Slice
architecture-review

## Reviewed Window
Fixed point: prior architecture-review commit `49da479`.

Reviewed product commits:
- `1edc65a` 005F2 deficiency return status contract hardening
- `6c259f9` 005FA member portal authentication
- `da34735` 005FB member portal dashboard/profile/supply
- `d1a12cf` 005G member portal application start/status

## Findings
1. High: suspended portal accounts are blocked at fresh login and portal data routes, but existing
   sessions can still expose portal claims through `/auth/me` because the shared session/current-user
   path validates only `UserSession` and `User.status`.
2. Medium: portal audit rows use implementation/internal action names instead of the source portal
   event names. Created corrective slice `005G2-member-portal-session-and-audit-contract-hardening`.
3. Pass: portal own-data object boundaries are carried through the reviewed slices.
4. Pass: reviewed tests are substantive and all gates pass.

Full wording is appended newest-first in `docs/working/REVIEW_FINDINGS.md`.

## Traceability
- Source says inactive/suspended portal users are blocked
  (`docs/source/screen-spec-member-portal.md` MP00 and §14.1). Current `/auth/me` and token payload
  code adds portal claims without checking `PortalAccount.status`; 005G2 requires a shared portal
  session-validity boundary and tests for old tokens after suspension.
- Source says portal critical actions use portal audit event names
  (`docs/source/screen-spec-member-portal.md` §11). Current portal auth/application code writes
  `portal.auth.*` and internal `applications.*` actions for borrower portal activity; 005G2 requires
  source-backed portal action names while preserving staff route audit names.
- Functional-spec M03 intake requirements were spot-checked. Borrower initiation/save/submit and
  deficiency/reference sequencing are partially implemented; nominee/signature/document upload,
  loan-limit, task assignment, and full staff intake frontend wiring remain queued/deferred.

## Evidence
- Review commits: `evidence/terminal-logs/review-window-commits.log`.
- Review diff summary: `evidence/terminal-logs/review-window-diff-stat.log`.
- Source extracts: `source-portal-session-audit-extract.log` and
  `source-functional-m03-extract.log`.
- Code snippets: `finding-portal-session-code-snippet.log`,
  `finding-portal-audit-code-snippet.log`,
  `finding-portal-application-audit-code-snippet.log`, and
  `finding-portal-audit-test-snippet.log`.
- Gate logs: backend/frontend logs under `evidence/terminal-logs/`.

## Gates
- Backend `manage.py check`: passed.
- Backend tests: 265/265 passed.
- Backend migrations check: passed.
- Backend coverage: 95%, floor 85.
- Frontend lint/typecheck/tests/build: passed; tests 90/90.
- `git diff --check`: passed.
- Protected-path scan: passed.

## Recommended Next Action
Run `005G2-member-portal-session-and-audit-contract-hardening`; after it passes, continue with
`005H-rejection-note-shell`.
