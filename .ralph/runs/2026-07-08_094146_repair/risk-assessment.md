# Risk Assessment

Risk level: Medium

## Why
- 004B adds a read-only authenticated member profile endpoint, one non-destructive migration, and
  frontend API wiring.
- Sensitive identifiers are present in the member domain, so masking and reveal deferral were
  treated as security-critical.
- The previous attempt failed only the Ralph changed-line limit; this repair keeps the diff below
  that limit.

## Controls
- `GET /api/v1/members/{member_id}/` requires session-bound bearer auth and `members.member.read`.
- PAN/Aadhaar responses are masked objects only: `{ masked, can_view_full: false }`.
- Full sensitive reveal (§13.5) is not implemented; no reveal controls are rendered.
- Masked profile reads create no workflow event and no profile-access audit row beyond normal login
  audit.
- Unknown/soft-deleted valid UUIDs return `404 NOT_FOUND`.
- Object-scope narrowing is recorded as A-030 because member ownership/team facts are not modeled
  yet.

## Gates
- Backend check/tests/migration sync/coverage passed.
- Frontend typecheck/lint/tests/build passed.
- `git diff --check` passed.
- Protected-path check passed.
- Diff-limit check passed: 19 files, 1724 changed lines excluding `.ralph/`.
