# Execution Plan

Selected slice: 006C2-cultivated-acreage-source-hardening

## Context

- Parent epic: `docs/epics/006-eligibility-loan-limit-appraisal.md`.
- Source references opened: functional-spec BR-020/BR-022 and M04-FR-006; API contracts §23.1-§23.3; data-model §10.2, §11.7-§11.8, §14.2, §35.1; test-plan MOD-LIMIT-002/008/009/010; A-049; architecture-review finding 2.
- Permission check: planned edits are within allowed paths (`sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`). No protected or forbidden paths will be edited.

## Plan

1. Add public API regression tests for loan-limit calculation:
   - selected verified owned land, application-linked verified crop plan, and profile cultivated acreage mismatch returns `400 VALIDATION_ERROR` with `error.field_errors.cultivated_acreage`;
   - mismatch preserves an existing stored snapshot and writes no `loan_limit.calculated` audit or `loan_limit_assessment` workflow event;
   - decimal-equivalent acreage values (`5`, `5.0`, `5.00`) calculate normally;
   - selected-land/crop-plan equality succeeds when profile cultivated acreage is null;
   - unverified/pending/rejected land or crop facts and null/wrong application crop links are blocked without success evidence.
2. Run the targeted backend test command with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and save the red output under `evidence/terminal-logs/`.
3. Implement the validation in the existing loan-limit service before any `LoanLimitAssessment.save()`, audit, or workflow event:
   - require selected land and crop facts to be verified, member-owned, and crop-plan linked to the current application;
   - compare normalized Decimal acreage values from selected land sum, crop-plan planned area, and profile cultivated acreage when present;
   - use the agreed acreage as the persisted `land_area_acres`.
4. Run the targeted tests again and save green output, then run required backend and frontend gates and save standard evidence.
5. Update API contracts/digest notes if the structured validation blocker contract needs durable documentation, then update run artifacts, handoff, state/progress, slice status, risk assessment, changed files, and review packet.
