# Execution Plan

Selected slice: `008F-power-of-attorney-workflow`

## Scope and interface

- Add the source-defined `SecurityPackage` and `PowerOfAttorney` persistence in `legal_documents`
  with one protected package per sanctioned application, one protected PoA per package, bounded
  status/execution fields, nullable-only pre-009C loan-account linkage, and database integrity for
  activation/release facts.
- Expose only §28.1-§28.3: package GET/refresh, package PoA POST/GET, and PoA PATCH. Do not add SH-4,
  CDSL, cheque, custody, invocation, release, checklist completion, readiness, or evidence download.
- Put package/PoA behavior behind one `legal_documents.modules.power_of_attorney` interface; retain
  parsing in the HTTP serializer adapter and consume stamp/notary/signature truth through
  legal-documents-owned selectors.

## TDD tracer sequence

1. RED/GREEN package refresh/read: sanctioned scope, permissions, fixed PoA-required pending package,
   exact replay, audit/workflow/version evidence, and checklist-preserving projection.
2. RED/GREEN draft PoA preparation: canonical application borrower/nominee, active Company Secretary
   attorney, retained purpose, current-renderer PoA document, one-PoA uniqueness, exact replay, and
   Compliance-vs-read-only authority.
3. RED/GREEN activation/change: Company Secretary-only activation, executed/effective facts, exact
   current document plus maker/checker adequate stamp/completed notary and canonical current borrower/
   nominee signed rows, stale/cross-application/legacy evidence rejection, immutable history, and no
   invocation/release/checklist/readiness side effects.
4. RED/GREEN nondisclosure and concurrency: unrelated/unknown ids, permission ordering, rollback on
   checklist projection conflict, and PostgreSQL five-worker create/change races retaining one current
   row with complete attributable history.

Each tracer writes a failing test first, captures RED output in `evidence/terminal-logs/`, then adds
only enough implementation to pass and captures GREEN output.

## Expected files

- `sfpcl_credit/legal_documents/models.py` and one new migration
- `sfpcl_credit/legal_documents/selectors.py`
- `sfpcl_credit/legal_documents/modules/power_of_attorney.py`
- `sfpcl_credit/legal_documents/serializers.py`, `views.py`, and `config/urls.py`
- identity permission-role catalogue only where required by the explicit Compliance/CS matrix
- focused backend API/module/PostgreSQL tests
- `docs/working/API_CONTRACTS.md`, assumption/digest notes only if source gaps require them

## Verification and closeout

- Run focused tests throughout, then Django check, migration sync, full backend coverage, and all
  frontend build/typecheck/lint/test gates with the mandated interpreters/tools.
- Save API examples, terminal logs, changed-files, risk assessment, review packet, and final summary.
- Review the implementation against the slice/source contract, sharpen the next one or two eligible
  Not Started slices using already-opened Epic 008 material, then update progress, handoff, state, and
  the selected slice status without running git add/commit/push.
