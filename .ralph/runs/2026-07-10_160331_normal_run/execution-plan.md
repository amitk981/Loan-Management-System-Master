# Execution Plan

Selected slice: 005I5-application-ownership-and-nominee-authority-hardening

## Scope and constraints

- Correct staff list/detail ownership projection to return `assigned_owner: null` until a persisted
  assignment/task owner exists; preserve intake actors, object access, and available actions.
- Consolidate the existing same-member/adult/age-evidence nominee decision behind one public backend
  module interface used by staff/portal draft mutation, submit/completeness/reference gates, and
  eligibility without changing the established error contract or age rule.
- Remove React age/minority decisions, surface backend `nominee_id` validation, render every safe
  nominee fact in portal detail, and keep sensitive nominee fields absent.
- Strengthen preservation and production-controller regressions. No task engine, new styling,
  source-document edit, or unrelated Epic 006 redesign is in scope.

## TDD tracer bullets

1. Add one staff list/detail API regression proving staff-created and portal-created applications
   expose neutral owner state; run it RED, then minimally correct the serializer projection and run GREEN.
2. Add one public nominee-validation module regression, then route one caller at a time through the
   interface (draft mutation, submit/completeness/reference, eligibility), running focused RED/GREEN
   cycles and preserving existing error behavior.
3. Add focused staff PATCH and portal create/PATCH blocked-mutation regressions for unknown,
   cross-member, minor, and missing-age-evidence nominees, asserting serialized detail/status and
   success audit/workflow counts remain unchanged; implement only corrections exposed by each test.
4. Add frontend regressions for selector-only form behavior and MP10 safe nominee rendering/sensitive
   absence; remove both client adult-evidence calculations and minimally extend existing markup.
5. Add a production `ApplicationDetail` loading/success/error/submit-refresh regression through
   mocked HTTP using the repository's existing test harness; avoid implementation-only view injection.

## Verification and evidence

- Save focused backend and frontend RED/GREEN terminal logs under `evidence/terminal-logs/`.
- Save staff/portal response examples and self-contained portal visual evidence under `evidence/`.
- Run backend check, migration-sync, full coverage gate with the mandated Ralph interpreter, plus
  frontend lint, typecheck, tests, and build; save outputs.
- Update API contract working documentation if the response/interface contract changes, then finish
  risk assessment, review packet, changed-files list, final summary, progress/state/handoff, slice
  status, digest, and sharpen the next one or two Not Started slices using already-opened sources.
