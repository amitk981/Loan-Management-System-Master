# Execution Plan

Selected slice: 003F-communication-template-shell

## Scope
- Implement only the content-template metadata/API shell from `docs/source/api-contracts.md` §39.1 and `docs/source/data-model.md` §24.1.
- Do not implement communication sending, delivery queues/retries, SMTP/SMS adapters, communication record listing, notification UI, document templates, or borrower/loan merge rendering.
- No frontend production code is in scope.

## Permission Check Before Edits
Planned editable paths are allowed by `.ralph/permissions.json`:
- `sfpcl_credit/**`
- `docs/working/**`
- `docs/slices/**`
- `.ralph/progress.md`
- `.ralph/state.json`
- `.ralph/runs/**`

Forbidden/protected paths will not be edited:
- `docs/source/**`
- `scripts/**`
- `.ralph/config.yaml`
- `.ralph/permissions.json`
- `AGENTS.md`
- `CLAUDE.md`
- `.gitignore`
- `docs/working/HIGH_RISK_APPROVALS.md`
- `docs/working/DECISION_POLICY.md`
- `docs/working/FRONTEND_DESIGN_RULES.md`

## TDD Plan
1. Add an integration-style backend test file for `GET/POST/PATCH /api/v1/content-templates/`, asserting the standard envelopes, metadata-only response fields, validation, audit rows, and 401/403 behavior.
2. Run the first targeted test before implementation and save the failing output as red evidence.
3. Add the `communications` Django app, `ContentTemplate` model, migration, service-layer validation/audit/pagination, and thin views/URLs to pass the tracer test.
4. Add remaining tests incrementally for create, patch, validation, duplicate code, unknown id, permission denial without writes, and security/no rendered merge output.
5. Run targeted green tests and then full backend gates.

## Implementation Notes
- Record the source permission gap in `docs/working/ASSUMPTIONS.md`.
- Use narrow content-template permissions, not `config.loan_policy.*`, `documents.template.*`, or communication-send permissions.
- Update `docs/working/API_CONTRACTS.md` with endpoint shape, fields, filters/pagination, permission assumption, validation errors, and audit actions.
- Update the epic digest with the final implementation note and deferrals.

## Verification and Closeout
- Run backend check, tests, makemigrations check, and coverage using `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.
- Run frontend typecheck, lint, tests, and build even though no frontend production code is expected to change.
- Save terminal logs, API response examples, `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Update `.ralph/state.json`, `.ralph/progress.md`, `docs/working/HANDOFF.md`, and mark the selected slice complete only after gates pass.
- Sharpen the next one or two `Not Started` slice files using only source/digest material already opened.
