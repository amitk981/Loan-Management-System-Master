# Execution Plan

Selected slice: `011J-archive-record-and-retention`

## Boundary and permissions

- Implement only the backend archive persistence, closure-module interface, scoped HTTP reads/write,
  audit, migration, and tests required by 011J. No frontend is in scope (011P owns it).
- Product edits will stay under `sfpcl_credit/**`; run evidence will stay under
  `.ralph/runs/2026-07-23_000144_normal_run/**`; an API-contract note may be added under
  `docs/working/**`. These paths are allowed by `.ralph/permissions.json`.
- Do not edit orchestrator-owned state/progress/slice status/changed-files/HANDOFF facts, protected
  workflow files, or `docs/source/**`.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command. Do not install
  dependencies, invoke Git mutations, run the complete backend suite, or run full coverage.

## Public interface and module shape

- Keep archive policy behind the existing `closure.modules.loan_closure.LoanClosureModule` seam,
  exposing archive creation/replay through that interface; views remain permission/scoping adapters.
- Preserve existing closure/NOC/security-return owners as immutable prerequisite evidence rather than
  duplicating their policy in callers.
- Add the source-shaped write endpoint and scoped manifest/detail read using the repository's standard
  response/error envelopes and action projection patterns.

## TDD tracer bullets

1. Inspect the existing closure model/module/routes/tests and archived-loan mutation guards, then add
   one public-behavior test for an eligible Compliance/CS actor archiving a closed loan. Save the
   focused failing output, add the minimum model/module/API/migration path, and save green output.
2. Add one behavior at a time for server-derived closure start and eight-calendar-year retention
   (including leap day), exact replay versus changed-location conflict, and prerequisite failures for
   missing NOC or applicable security return/unpledge. Save each meaningful red/green cycle.
3. Add scoped manifest/detail/search/read tests for authorised staff/Auditor and denials for wrong
   role/object scope/Borrower; verify audit payloads do not disclose archive paths.
4. Add archived-read-only and direct-mutation/early-destruction regressions, plus reverse-consumer
   checks that retained closure/NOC/security histories do not change.
5. Add the declared PostgreSQL concurrency acceptance test proving one archive manifest and one
   terminal status/history chain under five racing requests.

## Verification and evidence

- Run focused closure/archive tests after each tracer bullet, then affected closure/document/audit
  regression labels, Django `check`, and `makemigrations --check` with the mandated interpreter.
- Do not run the authoritative impacted/full backend lane; Ralph performs that independently.
- Inspect targeted diff hunks and diff stats, confirm protected paths are untouched, and save a
  manifest example plus concise terminal logs under the run evidence directory.
- Complete `risk-assessment.md`, `review-packet.md` with source-to-code-to-test traceability and Result
  exactly `Ready for independent validation`, and `final-summary.md`.
