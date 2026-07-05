# Execution Plan

Selected slice: 003E-versioned-configuration-shell

## Context Read
- Read `AGENTS.md`, Ralph token/context/runbook/config/permissions/state/handoff/policy/frontend rules, selected slice `003E`, parent epic `003`, and the existing epic digest.
- Opened only targeted source sections required by the slice:
  `data-model.md` §25.1 and §26.3, `api-contracts.md` §41.1 and §42.3,
  `functional-spec.md` M01-FR-001/M01-FR-002/M01-FR-015, and relevant permission catalogue lines.

## Permission Check
- Allowed edit areas for this slice: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`,
  `.ralph/state.json`, `.ralph/progress.md`, and `.ralph/runs/**`.
- Protected/forbidden files will not be modified: `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, and protected policy docs.

## Implementation Plan
1. Write one API-level failing test for the loan-policy config list endpoint before adding the app/model/view.
2. Add a `configurations` backend app with:
   - `LoanPolicyConfig` fields matching source §25.1 for this shell.
   - `VersionHistory` fields matching source §26.3.
   - One non-destructive migration.
3. Add a service boundary for loan-policy validation, serialization, pagination, draft create/update,
   activation, version-history write, and audit writes.
4. Add thin HTTP views and URL routes for:
   - `GET/POST /api/v1/config/loan-policy/`
   - `PATCH /api/v1/config/loan-policy/{loan_policy_config_id}/`
   - `POST /api/v1/config/loan-policy/{loan_policy_config_id}/activate/`
   - `GET /api/v1/version-histories/`
5. Continue TDD in small red/green cycles for create/audit, patch validation and state guard,
   activation/version history/audit, and version-history permissions/filter validation.
6. Update `docs/working/API_CONTRACTS.md`, assumptions if needed, slice status, handoff, progress,
   state, changed-files, risk assessment, review packet, and final summary.
7. Sharpen the next 1-2 `Not Started` slice files using only the source/digest material already opened.
8. Run required gates with the Ralph backend interpreter:
   `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python` for backend check,
   targeted/full tests, migrations check, and coverage; run frontend typecheck/lint/tests/build if present.

## Key Decisions
- Use `409 INVALID_STATE_TRANSITION` when patching a non-draft config, because that is a state guard rather than field validation.
- Use `400 VALIDATION_ERROR` when activation lacks `board_approval_reference`, because M01-FR-015 describes missing approval evidence.
- Retire any previously active loan-policy config on activation by setting its `status` to `retired` and `effective_to` to the day before the new config's `effective_from`; record this as an assumption if no more precise source rule is available.
- Do not implement M01-FR-003 through M01-FR-014 calculations/rules; only neutral storage fields from §25.1 are persisted in this shell.
