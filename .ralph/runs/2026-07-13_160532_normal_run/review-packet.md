# Review Packet: 2026-07-13_160532_normal_run

## Result

Implementation complete; local gates green and ready for independent Ralph validation.

## Slice

`007E-conflict-of-interest-blocking`

## Delivered behavior

- One approval-owned conflict module evaluates typed declarations and cycle-frozen maker facts.
- Ordered required authority remains immutable; unique exclusions overlay frozen same-role
  alternates and preserve matrix role/count requirements.
- Missing frozen authority closes as `blocked_by_conflict`; Director/relative conflicts set the
  downstream general-meeting-evidence flag.
- Excluded actors retain limited read only. Approve/reject/return use the exact source conflict
  error and create the narrowly attributable COI-006 denial audit without other writes.
- `POST .../abstain/` records an immutable reasoned action and either reassigns a frozen alternate
  or creates a communication-backed blocked outcome.
- New cycles recompute from their own facts; historical exclusions/actions remain attached to the
  prior case id and cycle.

## Traceability

- The source says conflicted users must be excluded, reasons recorded, attempted approval denied
  and audited (`auth-permissions.md` §17.1-17.3, COI-001..006). The code freezes exclusions in
  `ConflictOfInterestModule`/`SanctionHandoffModule` and denies through `record_action`; verified by
  `test_enrichment_freezes_exclusions_without_rewriting_authority_snapshot`,
  `test_conflicted_approval_returns_exact_source_error_and_denial_audit`, and
  `test_every_conflicted_write_path_uses_one_exact_denial_contract`.
- The source says approval exclusion/replacement cannot reduce required authority
  (`security-privacy.md` §12.2-12.3). The code derives alternates only from the frozen committee and
  blocks an unsatisfied role; verified by
  `test_frozen_alternate_director_satisfies_original_role_count_after_exclusion` and
  `test_unsatisfiable_abstention_blocks_case_without_creating_sanction`.
- The source requires abstention and general-meeting evidence for Director/relative cases
  (`functional-spec.md` M05-FR-011/012). The immutable action ledger accepts `abstained` and
  enrichment projects `general_meeting_evidence_required`; verified by
  `test_conflict_abstention_uses_immutable_action_and_assigns_frozen_alternate` and
  `test_conflict_module_maps_declared_relationship_and_interest_facts`.
- The source module seam is `approvals.modules.conflict_of_interest`
  (`codebase-design.md` §13.2); the implementation uses that exact boundary and frozen cycle facts,
  verified by `test_conflict_module_uses_frozen_cycle_maker_facts`.

## Validation

- Focused approval: 70 passed, 2 expected PostgreSQL-only skips.
- Backend: Django check and migration sync pass; 637 passed, 19 expected PostgreSQL-only SQLite
  skips; 93% coverage (floor 85%).
- Frontend: build, typecheck, lint, 208 tests pass.
- Diff/protected review: `git diff --check` passes; no protected or `docs/source` changes.
- Evidence: `evidence/terminal-logs/` and `evidence/conflicted-approver-error.json`.

## Review focus

Inspect the immutable authority overlay, denial-audit transaction boundary, migration maker-fact
backfill, and the explicit A-082 relationship-source assumption. Independent validation may
proceed; the next queue event is the due architecture review.
