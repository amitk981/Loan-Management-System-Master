# Review Packet: 2026-07-23_220436_repair

## Result
Ready for independent validation

## Slice
011O-auditor-read-only-views

## Repair finding

The saved backend coverage failure was caused by a stale reverse-consumer test fixture, not by an
incorrect production permission rule. The global compliance-search matrix created a new
`internal_auditor` role with read permissions but no persisted `audit_readonly` scope, so the 011O
fail-closed scope guard correctly rejected it.

## Repair completed

- Added an active `ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY` grant to the global-search test
  actor's exact role.
- Preserved the production scope guard and the separate inactive-scope denial coverage.
- Changed no product code, schema, routing, frontend, dependency, or protected/source file.

## Source-to-code traceability

- `docs/source/auth-permissions.md` §§15.11, 19.1, and 26.7 say Internal Auditor receives broad
  read-only access through `audit_readonly` scope and no operational authority. The production code
  requires that active persisted scope, and
  `GlobalSearchComplianceTests.test_compliance_cfo_cs_and_auditor_permission_matrix` now constructs
  a valid scoped auditor before verifying safe compliance-search cards.
- `docs/source/auth-permissions.md` §§19.4 and 22 require document-category and sensitivity controls.
  The same global-search matrix verifies that restricted evidence text is absent and evidence cards
  expose no quick action.
- `docs/source/security-privacy.md` §34 requires read-only internal-audit access while compliance
  details remain owner/auditor scoped. The adjacent 011O API suite verifies active-scope access,
  inactive-scope 403s, action-free projections, and zero operational mutation authority.

## Evidence

- `evidence/terminal-logs/global-search-auditor-red.log`: exact behavior reproduced with
  `ComplianceDenied` for the unscoped auditor.
- `evidence/terminal-logs/global-search-auditor-green.log`: the same behavior test passed after the
  fixture repair.
- `evidence/terminal-logs/auditor-search-scope-focused-green.log`: 11 adjacent global-search and
  011O auditor API tests passed.
- `evidence/terminal-logs/backend-coverage-exact-validator-green.log`: exact authoritative validator
  passed 1,728 tests with 175 expected skips and 89% coverage against the 85% floor.
- `evidence/terminal-logs/backend-coverage-native-architecture-note.md`: records the established
  native-arm64 multiprocessing handoff used for the successful exact rerun.

## Independent validation boundary

The agent reran the exact failed coverage validator successfully. Ralph must still perform its full
independent validation of the preserved candidate and commit only if every selected gate remains
green.

## Recommended Next Action

Run independent validation. Commit only after all Ralph gates pass.
