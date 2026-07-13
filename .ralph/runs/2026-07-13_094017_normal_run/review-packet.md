# Review Packet: 2026-07-13_094017_normal_run

## Result
Ready for independent validation

## Slice
007C-cfo-and-director-threshold-routing

## Recommended Next Action
Run Ralph independent validation and, if green, let the orchestrator commit and merge to staging.
The four-slice architecture review is due before 007D.

## Traceability

- API §25.3 says list cases with status/type/assignment filters; `list_approval_cases` supplies
  strict filters and pagination, verified by
  `test_list_filters_are_strict_and_preserve_the_exact_threshold_route`.
- API §25.4 and §44 say detail exposes required decisions, exclusions, and action availability;
  `serialize_case_detail` reads immutable actions and projects approve/reject/return with separate
  permissions, verified by `test_assigned_approver_detail_projects_snapshot_actions_and_review_facts`
  and `test_assignment_does_not_replace_each_action_specific_permission`.
- Auth §12.6/§16.2 says case read and stored authority govern access; HTTP views enforce read while
  the engine uses only stored required/excluded/action facts. Global-reader, maker, unrelated,
  CFO, and Director rows are verified by the focused public API tests.
- Functional M05-FR-002 says show eligibility, amounts, purpose, compliance, borrowing history,
  risk, and documentation completeness; `_review_facts` reads those owners dynamically, verified
  by `test_review_facts_are_read_through_projections_from_the_owning_records`.
- 007B sharpening says version-1 or incomplete snapshots cannot route and current configuration
  cannot rewrite history; missing-provenance and simultaneous routed/shell tests verify both.

## Two-Axis Review

### Standards

Initial review found unfinished Ralph artifacts and three unused decision constants; those are
resolved in this packet/state/handoff/status update and by removing the constants. It also noted
view-owned permission policy and Python-side pagination as judgement calls. The permission remains
at the authenticated HTTP boundary, while the database now prefilters every scalar routed fact
before JSON snapshot validation; no documented standard requires a reusable non-HTTP permission
exception or database-specific JSON query.

### Spec

Initial review found authority was being re-derived from stored matrix/committee projections,
contradictory historical coverage was partial, and nullable action fields diverged from §15.4.
Corrected: required snapshot items alone control assignment; a routed case and same-amount unrouted
shell remain stable across live changes; comments/IP/user-agent are nullable. The optional signature
target does not yet exist, so its nullable UUID reference is explicitly governed by A-077 until the
signature-record owner lands.

Summary: Standards review reported 3 hard/2 judgement findings and Spec review reported 1 high/2
medium findings. All slice-blocking findings were corrected; the signature FK dependency is an
explicit recorded follow-up rather than an invented cross-epic model.

## Validation

- Backend: 566 tests pass, 16 expected PostgreSQL-only skips; coverage 93%; check and migration
  sync pass.
- Frontend: build, typecheck, lint, and 208 tests pass.
- Focused: 13 routing API tests plus 46 approval regressions pass (five expected PostgreSQL skips).
- Diff limits: one migration, no dependencies, within 30 files and 2,000 lines.
