# Execution Plan: 006B Default Document Purpose and Terms Eligibility Checks

## Scope
- Extend the existing 006A eligibility assessment run/read API; do not add endpoints.
- Compute default, document, terms acceptance, purpose, and nominee checks from existing source-backed fields.
- Preserve the 006A state guard, `credit.eligibility.run`, object access, one-to-one rerun behavior, metadata-only audit/workflow evidence, and no success evidence on denied or invalid paths.

## Source Trace
- `api-contracts.md` section 22.1 expects `default_check=no_default`, `document_check=complete`, `terms_acceptance_check=accepted`, `purpose_check=agriculture_aligned`, `nominee_check=valid`, and `overall_result=eligible` when all checks pass.
- `data-model.md` sections 13.1 and 14.1 provide `purpose_category`, `terms_acceptance_flag`, and eligibility check result fields.
- `functional-spec.md` BR-008, BR-009, BR-013, BR-014, BR-018 require no default, adult nominee, required documents, and agriculture/crop purpose.
- Existing digest says use 005D/005E checklist metadata and do not invent a nominee-selection rule when application nominee identity is unavailable.

## Permission Check
- Editable paths required for this slice are allowed by `.ralph/permissions.json`: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, and `.ralph/runs/**`.
- Protected and forbidden paths will not be modified: `scripts/`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, guarded policy docs, and `docs/source/**`.

## TDD Plan
1. Add a focused API test proving a fully sourced application returns pass/eligible checks instead of 006A pending values.
2. Run the focused test with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and save the RED output.
3. Implement the minimal eligibility check composition in `applications/services.py`.
4. Add/adjust tests for blocker paths: active default, missing/failed checklist metadata, non-agriculture purpose, missing terms acceptance, and application-specific minor nominee evidence.
5. Verify rerun, permission/object/invalid-state behavior remains covered.
6. Update `docs/working/API_CONTRACTS.md` and the slice status/checklist.

## Gates and Evidence
- Save red/green focused test logs under `.ralph/runs/2026-07-10_052139_normal_run/evidence/terminal-logs/`.
- Run backend check, backend focused/full tests, migrations check, backend coverage, frontend lint/typecheck/tests/build, and `git diff --check`.
- Save changed files, risk assessment, review packet, final summary, state/progress/handoff updates, and sharpen the next 1-2 Not Started slices from already opened source/digest context.
