# Review Packet: 2026-07-11_143648_normal_run

## Result
Pass

## Slice
006G4-sanction-dependency-boundary-regression

## Recommended Next Action
Allow independent Ralph validation and commit, then run 006H5.

## Change Summary

- Replaced the narrow import-name collection in the sanction architecture regression with a
  package-aware AST resolver.
- Added an explicit allowlist containing only the documented public appraisal-workflow handoff.
- Added synthetic direct, aliased, package-level, package-exposed, private, and public fixtures.
- Made the repository scan non-vacuous by requiring the public approvals-to-credit edge.
- Production files were not changed.

## Traceability

- The source design says dependencies must follow documented module direction and that circular
  dependencies indicate a misplaced seam (`codebase-design.md` §12.3, §13.1, §36.2).
- ADR-0005 says approvals may depend on credit's public appraisal interface while credit must not
  import approvals.
- The tests enforce exactly that direction through
  `test_business_app_dependency_direction_is_approvals_to_credit_only`, with syntax coverage in
  `test_dependency_import_collector_resolves_package_and_alias_forms` and allowlist behavior in
  `test_dependency_guard_rejects_forbidden_forms_and_allows_public_handoff`.

## Validation

- RED: current collector missed `from sfpcl_credit import approvals`; saved in
  `evidence/terminal-logs/tdd-red.txt`.
- Focused sanction suite: 12 tests passed, one expected PostgreSQL-only skip.
- Frontend: lint, typecheck, build, and 144 tests passed.
- Backend: Django check, migration sync, and 396 tests passed at 94% coverage.
