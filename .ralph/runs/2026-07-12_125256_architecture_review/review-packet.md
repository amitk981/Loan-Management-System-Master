# Review Packet: 2026-07-12_125256_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Review Window

Pinned at `git diff cea56b2...HEAD`: 006X4 (`a75010c`), 006Y3 (`7668c72`), 006Y4
(`f2ea8d1`), and 006Z (`cd6822f`). Orchestrator-only commits `62f8d89` and `8cd5f45` were excluded.
Production code was not changed by this review.

## Standards Axis

- High: 006X4's new matrix projects five appraisal actions but executes only one denied update;
  enabled writes, eligibility/limit/create/review variants, authority/state coverage, and a stale-
  projection race remain absent.
- High: Member Registry is a shallow/bypassable seam, lacks internal object access/read, and can
  surface an uncaught unique-constraint error when approving a duplicate protected identity.
- High: witness actions omit disabled permission/object facts, so projection/write parity is not
  representable or tested.
- High: credit imports member supply persistence and owns/tests a private active-status rule instead
  of consuming `members.modules.active_member_status`.
- High-risk judgment: supply capture does not validate known fields, year/entity/route/reference
  consistency, UUIDs, or decimal constraints before persistence.

## Spec Axis

- High: 006X4 did not deliver its enumerated enabled/disabled public action/write acceptance matrix.
- High: 006Y3 enables approval for a requester holding checker permission even though the write
  rejects them, and the form omits most API §13.2 individual/institution fields.
- High: 006Y4 omits S09 witness address/mobile correction.
- High: 006Z can pass BR-004 with a legacy active flag while persisted services are false; capture
  lacks the sharpened optimistic member version and eligible entity/route boundary.

## Corrective Work and Traceability

Created High-risk 006X5, 006Y5, 006Y6, and 006Z3. 006Z2 now depends on 006Z3. Epic 004/006 digests,
the implementation index, REVIEW_FINDINGS, state, progress, and handoff were updated. M02-FR-012,
M02-FR-004/BR-004/BR-007, and the exhaustive M04-FR-004..011 regression claim remain open to those
correctives; M02-FR-009 shareholder validation remains substantive while S09 correction is partial.
No ADR or CONTEXT change was needed because existing source/module rules already settle direction.
No Blocked slice was stale.

## Validation

- Frontend lint/typecheck/build and 173 tests passed.
- Backend check/migration sync and 423 tests passed with five expected skips at 94% coverage.
- Slice queue lint, Ralph workflow regressions, JSON, `git diff --check`, protected-path, and
  production-code-unchanged checks passed. The first queue-lint shell wrapper used zsh and hit its
  read-only `status` variable; the exact gate was rerun successfully under Ralph's bash shell.
- Logs: `evidence/terminal-logs/frontend-gates.log`, `backend-gates.log`, and
  `review-doc-gates.log`.

## Recommended Next Action
Validate and commit this docs-only review, then run 006X5, 006Y5, 006Y6, and 006Z3 before 006Z2.
