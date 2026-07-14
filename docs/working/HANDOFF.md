# Ralph Handoff

## Last Run

2026-07-14_102642_normal_run

## Current Status

008B2 is complete. `legal_documents` is now the single runtime owner of the retained
`loan_documents` model/table, generation module, HTTP adapters, and exact application-scoped
collection selector. The foundation `documents` package imports no application/approval/legal
business owner and continues to own template files, provenance, and storage only.

Direct and HTTP callers cross the same active-actor, generate/read permission, template-reference,
application-scope, state, replay, and evidence boundary. The single state-only ownership migration
retains existing rows and adds a database `loan_account_id IS NULL` constraint under A-102 until
009C installs the real protected loan FK.

## Validation

Evidence is in `.ralph/runs/2026-07-14_102642_normal_run/evidence/`. Frontend build, typecheck,
lint, and all 293 tests pass. Django check/migration sync and all 732 backend tests pass with 22
expected skips at 93% coverage. The 21 focused legal-document tests, fresh migration, retained-row
migration test, authority/dependency matrices, and two post-review PostgreSQL race runs pass.

## Next Run

Run 008B3, then 008C. Both are sharpened against the completed legal owner: the renderer stays
behind the public module and proves genuine DOCX/PDF content, while checklist work consumes only
legal-selector metadata and preserves A-102 until 009C.
