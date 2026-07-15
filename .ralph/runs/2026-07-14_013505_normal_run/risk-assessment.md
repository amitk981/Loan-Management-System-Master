# Risk Assessment

Risk level: High

- Selected slice: `007K-frozen-review-snapshot-and-selector-boundary-closure`
- Mode: `normal_run`
- Standing approval: active; no `[revoked]` entry exists.

## Security and integrity

- Approval review truth is now projected by the credit owner while application, appraisal,
  immutable review history, and risk rows are locked. Approvals persists the returned object and
  never repairs it from later mutable rows.
- Canonical reads require the full typed review schema, a persisted immutable review-decision link,
  matching reviewer/provenance identity, UUID identifiers, a timezone-aware assessment timestamp,
  exact application references, and amount/provenance consistency. A stale true coherence flag or
  reader index remains narrowing only and cannot authorize disclosure.
- Collection/detail/actions/sanction decision/Exception Register/Credit Sanction Register fail
  closed before filters, counts, pagination, serialization, or ledger writes when review truth is
  empty, partial, malformed, or inconsistent.
- The selector no longer imports or executes approval policy. One approval-owned read decision
  combines frozen validity and attributable actor scope; register callers cannot bypass it.

## Migration and operational risk

- No schema or data migration was added. Legacy 0011/0012 reconstructions are recognized as
  unproven because they lack the new credit-owned schema/review-decision provenance marker and
  therefore remain nondisclosing. The isolated worktree has no migrated `approval_cases` table, so
  no retained local row could be inspected and no mutable later truth was copied.
- No signal, model-save side effect, dependency, frontend production change, external call, or
  protected/source-file edit was introduced.
- Tests cover stale projections, all public boundaries, zero-write denial, live-record mutation,
  terminal history, corrected cycle 2, dependency direction, and bounded coarse candidate work.

## Gate outcome

- Backend: Django check and migration sync pass; 685 tests pass with 19 expected PostgreSQL-only
  SQLite skips; coverage is 93% against the 85% floor.
- Frontend: build, typecheck, lint, and 251 tests pass unchanged.
- Diff: `git diff --check` and queue lint pass; 14 tracked files / 1,130 changed lines are within
  configured limits; no protected path, dependency, or migration changed. Independent
  Standards/Spec findings were addressed before the final gate.
- Manual review required: orchestrator independent validation before commit/merge/push.
