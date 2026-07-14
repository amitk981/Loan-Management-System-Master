# Review Packet

## Outcome

Slice 008I2 is complete and ready for independent Ralph validation.

## Review Focus

- Confirm the 510-line PoA policy moved intact to the security owner and the legal compatibility
  module contains no policy, dynamic binding, or attribute forwarding.
- Confirm exact ₹500.00 is PoA-specific and the generic stamp recorder/Loan Agreement rule did not
  change.
- Confirm package GET scope for direct Stage-4 readers, assigned CFO/Director approvers, and
  persisted auditors; unrelated approvers and read-only mutations must remain denied.
- Confirm retained tables, ids, relations, v1 routes, replay, legacy activation, checklist
  projection, generated-document provenance, and terminal evidence did not change.
- Confirm both PostgreSQL runs retain one exact activation winner and no loser/downgrade success
  identities.

## Traceability

- The source says `security_instruments` owns PoA and rejects pass-through modules
  (`codebase-design.md` §§8.2, 28.1, 36.2); the code defines every PoA public function in the
  security module, verified by
  `SecurityInstrumentBoundaryTests.test_security_app_is_the_real_power_of_attorney_policy_owner`.
- The source says PoA requires ₹500 stamp and notarisation (`functional-spec.md` M06-FR-008; V10
  p.14 §4.3); the code checks `Decimal("500.00")` in the atomic activation validator, verified by
  `test_company_secretary_activates_only_with_current_maker_checker_and_signatures` for ₹1,
  ₹499.99, ₹500.01, and ₹500 success plus zero-write failures.
- The source says scoped Credit/Finance/CFC/CFO/Director/Auditor roles may read security metadata
  while CS/Compliance own mutation (`auth-permissions.md` §§14.1, 16.4, 19.2-19.4); the code splits
  read permission, canonical scope, and mutation roles, verified by
  `test_package_read_role_and_object_scope_never_grants_mutation_or_reveal` and the catalogue test.

## Validation

- TDD: retained red/green module-owner, exact-stamp, read-matrix, and catalogue logs.
- Focused: 27 PoA/ownership/catalogue tests green; impacted SH-4/CDSL cluster green with expected
  PostgreSQL-only skips.
- PostgreSQL: changed activation and downgrade races green twice with strengthened identity checks.
- Backend: Django check and migration sync green; 829 tests green, 36 expected skips, 92% coverage.
- Frontend unchanged: lint, typecheck, build, and 293 tests green.
- Visual/browser acceptance: not applicable to this backend-only slice.
- Diff: 15 tracked files, 1,577 tracked changed lines before run artifacts; below 30 files/2,000
  lines, with no new dependency or migration.

Evidence: `.ralph/runs/2026-07-15_001106_normal_run/evidence/`.
