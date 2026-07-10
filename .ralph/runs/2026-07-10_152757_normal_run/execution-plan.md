# Execution Plan

Run: `2026-07-10_152757_normal_run`  
Selected slice: `006D2A-credit-eligibility-module-and-configuration-seam`

## Scope and interface

- Establish the source-named `sfpcl_credit.credit` Django package and the public
  `credit.modules.eligibility_assessment.EligibilityAssessmentModule` seam.
- Move eligibility lookup, validation, rule evaluation, transaction/locking, persistence,
  audit/workflow coordination, serialization snapshot, and public result/error types out of
  `applications.services` behind that seam.
- Establish `configurations.modules.configuration_resolver.resolve_effective_loan_policy` as the
  only active/effective loan-policy lookup and validation seam, while leaving the loan-limit
  calculation and snapshot implementation in `applications.services` for slice 006D2B.
- Keep HTTP payloads/statuses, permissions, object access, rerun semantics, audit/workflow metadata,
  database models/tables/migrations, frontend code, and dependencies unchanged.

## TDD and implementation sequence

1. Run the existing eligibility and loan-limit characterization tests and save the green baseline.
2. RED: add focused public-module tests for eligible/ineligible/pending results, rollback behavior,
   resolver delegation, and the application-view import boundary; save the failing output.
3. GREEN: add the credit package/common result types, eligibility module, configuration resolver,
   and thin view delegation; remove only the migrated eligibility helpers from
   `applications.services` and route its existing loan-policy lookup through the resolver.
4. Run the focused module/API tests after each vertical behavior is made green; save the final
   focused green output. Confirm loan-limit tests remain green and no migration is generated.
5. Refactor only while green, checking that callers/tests cross the same small public interface and
   that no private eligibility helper remains importable from `applications.services`.

## Validation and completion

- Run backend check, migration sync, full coverage suite with the mandated Ralph Python interpreter,
  then frontend lint, typecheck, tests, and build, plus `git diff --check`.
- Keep the implementation below the slice target of 1,400 changed lines and the hard Ralph limits;
  do not include any 006D2B loan-limit extraction.
- Save self-contained terminal evidence, changed-files list, risk assessment, review packet, and
  final summary in this run folder.
- Update the selected slice status, `.ralph/state.json`, `.ralph/progress.md`, `HANDOFF.md`, and the
  Epic 006 digest. Sharpen the next one or two Not Started slices using only already-opened sources.
- Do not run `git add`, `git commit`, or `git push`; the orchestrator owns validation and integration.
