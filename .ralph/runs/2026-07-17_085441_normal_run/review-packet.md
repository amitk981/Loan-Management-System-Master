# Review Packet: 2026-07-17_085441_normal_run

## Result
Agent implementation complete; independent validation pending.

## Slice
009D4-readiness-effective-role-and-signature-scope-closure

## Outcome

- Readiness authorization now uses active `effective_role_codes`, requires the explicit readiness
  permission, and unions the canonical object scopes for all effective source reader roles.
- Signature readiness now queries only latest current documents for applicable required PoA,
  tri-party, SH-4, Term Sheet, and Loan Agreement items. Exact signer and mismatch evidence remains
  fail-closed inside that set.
- The public endpoint, 23 checks/order, reasons, secrets, query ceiling, and zero-write behavior are
  unchanged.

## Traceability

- The source says Senior Manager Finance/CFC/Credit Manager/CFO/Auditor can read Stage-5 readiness
  only within their loan scopes (`auth-permissions.md` §§15.6-15.8, 19.3, 26.5); the code resolves
  central active effective roles and ORs only those canonical scopes; verified by
  `test_active_governed_cfo_with_explicit_grant_receives_portfolio_scope`,
  `test_multi_role_scope_is_the_union_when_primary_senior_finance_is_unassigned`, the governed CFC
  initiation test, and the retained source-reader matrix.
- The source says only the required current documentation/signatures block disbursement
  (`screen-spec.md` S32-S35/S38; `functional-spec.md` M06-FR-019 and M08-FR-001-004); the code filters
  to the latest applicable five document families while retaining exact signers; verified by the
  unrelated-signature RED/GREEN probe and the five-family extra/wrong signer matrix.

## Verification

- Backend: 34 focused tests pass; four named zero-write/query/scope proofs pass; Django check and
  `makemigrations --check --dry-run` pass.
- Frontend unchanged: ESLint, TypeScript, all 327 Vitest tests, and Vite build pass.
- Evidence: `evidence/role-scope-matrix.md`, `evidence/exact-signer-matrix.md`,
  `evidence/query-zero-write-proof.md`, and `evidence/terminal-logs/`.
- Complete backend coverage was intentionally not run locally; Ralph performs it independently.

## Reviewer focus

- Confirm that explicit readiness permission through the actor's active primary-role grant is the
  intended permission seam while governed authority supplies the additional effective role.
- Confirm the Auditor grant is tied specifically to the active `internal_auditor` catalogue role.
- Confirm no non-readiness signature document type belongs in the five-family blocker set.

## Recommended Next Action
Run independent Ralph validation and coverage; if green, commit/merge this slice, then execute 009E2.
