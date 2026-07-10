# Review Packet: 2026-07-10_125342_normal_run

## Result
Success

## Slice
006C2-cultivated-acreage-source-hardening

## Summary

Hardened loan-limit calculation so BR-020 cannot silently use all selected owned acreage when
cultivation evidence is lower or unresolved. Calculation now requires:

- selected land holdings are member-owned and `verified`;
- selected crop plan is member-owned, `verified`, agriculture aligned, and linked to the current
  loan application;
- normalized Decimal acreage values agree across selected land total, crop-plan planned acreage,
  and profile cultivated acreage when present.

On disagreement, the endpoint returns `400 VALIDATION_ERROR` with
`error.field_errors.cultivated_acreage = "CULTIVATED_ACREAGE_UNRESOLVED"` before any assessment,
audit, or workflow evidence is written.

## Traceability

- Source says BR-020 land limit must use land area under cultivation
  (`docs/source/functional-spec.md` BR-020), and §23.2 keeps the land formula as
  scale-of-finance multiplied by acreage.
- Source schema exposes selected land acreage, crop-plan planned acreage, and nullable profile
  cultivated acreage but does not define precedence (`docs/source/data-model.md` §10.2, §11.7,
  §11.8, §14.2, §35.1).
- Code now blocks unresolved disagreement in `sfpcl_credit/applications/services.py` before save/
  audit/workflow, then stores the agreed value as `land_area_acres`.
- Tests prove mismatch blocking, Decimal normalization, null-profile two-value success, pending/
  rejected and unlinked evidence blockers, and failed-rerun snapshot preservation in
  `sfpcl_credit/tests/test_loan_applications_api.py`.

## Evidence

- Red test: `evidence/terminal-logs/red-cultivated-acreage-mismatch.log`
- Green targeted test: `evidence/terminal-logs/green-cultivated-acreage-mismatch.log`
- Focused API suite: `evidence/terminal-logs/backend-application-api-green.log`
- Full backend tests: `backend-test-results.md` (301 tests)
- Coverage: `backend-coverage-results.md` (95%, floor 85%)
- Backend check: `backend-check-results.md`
- Migration sync: `backend-migrations-results.md`
- Frontend lint/typecheck/test/build: `lint-results.md`, `typecheck-results.md`,
  `test-results.md`, `build-results.md`
- API examples: `api-examples.md`
- Diff hygiene: `diff-check-results.md`

## Recommended Next Action
Run `006D2-credit-assessment-deep-module-boundary`, then `006E-appraisal-note-create-edit-submit`.
