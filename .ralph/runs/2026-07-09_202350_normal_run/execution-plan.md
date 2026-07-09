# Execution Plan: 005E-completeness-workbench

## Scope
- Backend/API-only slice unless existing contracts reveal required frontend wiring. Source and slice text allow backend/API first for 005E.
- Add a derived completeness workbench read endpoint for submitted loan applications.
- Add a completeness pass endpoint that blocks until latest mandatory 005D checklist metadata is verified, then delegates to the existing 005C reference-generation service.
- Do not implement deficiency records, eligibility, loan limit, appraisal, sanction, disbursement, or frontend redesign.

## Source Basis
- `screen-spec.md` S12: completeness verifies submitted applications before official `LO...` reference generation; all mandatory checks must pass.
- `screen-spec-member-portal.md` MP08: borrower receives reference number after submitted details/documents are checked.
- `implementation-roadmap.md` §11: completeness APIs mark complete/incomplete and create deficiencies; deficiency creation is broader and deferred here.
- 005D digest: required application checklist document codes are derived from application-document metadata.

## Permission And Protected-Path Check
- Editable implementation paths are allowed by `.ralph/permissions.json`: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`, `.ralph/runs/**`.
- Forbidden/protected paths will not be modified: `docs/source/**`, `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, high-risk/design/decision guardrails.

## TDD Plan
1. RED: Add API regression for workbench read showing checklist statuses and `can_generate_reference = false` while required latest metadata is missing/non-verified.
2. GREEN: Add service serialization and `GET /completeness-check/`.
3. RED: Add completeness pass regression for all required latest items verified, expecting `LO...` reference/register through existing 005C path.
4. GREEN: Add `POST /completeness-check/pass/` that validates checklist then delegates to `generate_reference_after_completeness_pass(...)`.
5. RED: Add validation/permission/scope regressions for incomplete checklist, draft/duplicate state, missing permissions, and same-permission object-scope denial with no side effects.
6. GREEN/refactor: Consolidate checklist failure shaping and response serialization without adding database schema.

## Quality Gates
- Focused backend test during TDD with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Full backend gates: `manage.py check`, tests, `makemigrations --check --dry-run`, coverage floor.
- Frontend gates because Ralph requires them: `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`.

