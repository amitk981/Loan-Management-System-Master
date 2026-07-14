# Execution Plan

Selected slice: `008B2-legal-document-generation-boundary-closure`

## Outcome

Move the retained loan-document model, generation orchestration, and collection read boundary into
the source-defined `legal_documents` app while preserving the public v1 routes, the existing
`loan_documents` database table and rows, exact replay/evidence semantics, and the 008A2 template
variant/file-reference decisions.

## Constraints and decisions

- Backend-only slice; no frontend or `docs/source/` changes.
- Keep `documents` as the foundation file/template/storage owner and remove its imports of
  application/approval business modules.
- Keep one writable Django owner for `loan_documents`; use state-only ownership migration where
  possible so retained rows are not copied or rewritten.
- Until Epic 009 installs the real loan aggregate, replace the unconstrained nullable UUID with a
  database constraint that permits only `NULL`; record the deferred FK handoff to 009C.
- HTTP views remain transport adapters and call the same authority-enforcing public module used by
  direct callers.
- All backend commands use `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.

## TDD tracer bullets

1. Add a direct generation-module authority matrix covering inactive actor, missing generate
   permission, missing template-reference permission, and missing application object scope. Run it
   RED and retain the output, then move/enforce the public legal boundary until GREEN.
2. Add direct and HTTP read-boundary tests proving read permission plus object scope is applied
   before exact count/page/serialization, including deterministic first/middle/final/empty pages.
   Run RED, then move query shaping and pagination into the legal selector until GREEN.
3. Add import/dependency tests proving `documents` imports no application/approval business owner
   and the public legal module imports no view/HTTP request type. Run RED, then complete the module,
   model, view, and import ownership move until GREEN.
4. Add migration/model tests for retained table identity and database-enforced nullable-only
   `loan_account_id`. Run RED, then add the single non-destructive migration and reach GREEN.
5. Re-run focused replay/storage/audit/workflow tests and the PostgreSQL five-request race twice to
   prove the ownership move preserved one canonical result and evidence set.

## Verification and evidence

- Save every RED/GREEN command under `evidence/terminal-logs/` and sanitised API/authority/
  dependency/migration summaries under `evidence/`.
- Run Django check, migration sync, the focused suite, full backend coverage, and all configured
  frontend build/typecheck/lint/test gates.
- Review the complete diff against this slice and documented standards, then write
  `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Update API/assumption documentation only if the public contract/deferred state requires it;
  finish by updating slice status, state, progress, and handoff, and sharpen the next one or two
  eligible Not Started slices using only source material already opened.
