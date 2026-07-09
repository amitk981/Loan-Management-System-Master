# Execution Plan: 005F2 Deficiency Return Status Contract Hardening

## Scope
- Backend/API only. No frontend changes.
- Correct deficiency return state from `submitted` to source-backed `incomplete_returned` while preserving 005F no-reference/no-register/no-sequence/no-credit-assessment guarantees.

## Source Contract
- `docs/source/data-model.md` lists `loan_application_status = incomplete_returned`.
- `docs/source/functional-spec.md` M03 deficiency flow says incomplete applications enter the incomplete state and retain deficiency history.
- `docs/source/screen-spec.md` S12 says returned applications become `Incomplete - Returned to Applicant` or rejected.
- Source docs do not define repeat returns from `incomplete_returned`; keep them blocked and record the assumption.

## Implementation Steps
1. Inspect existing application model/service/tests for deficiency return behavior.
2. TDD red: update focused backend tests so successful return must respond and persist `application_status = incomplete_returned`, audit/workflow show `submitted -> incomplete_returned`, and repeat return is blocked without duplicate side effects.
3. Green: add `LoanApplication.STATUS_INCOMPLETE_RETURNED`, include it in validation vocabulary, and update `return_application_with_deficiencies(...)` to set/serialize/audit/workflow the new state.
4. Update `docs/working/API_CONTRACTS.md`, the epic 005 digest, ASSUMPTIONS, progress/handoff/state, slice status, and run artifacts.
5. Run focused backend tests and required quality gates with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for backend commands; save logs under evidence.

## Permissions Check
Allowed edit paths from `.ralph/permissions.json`: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`, `.ralph/runs/**`.
Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, `.git/**`.
