# Execution Plan

Selected slice: 008C-documentation-checklist-applicability

## Scope and authority

- Implement only the post-sanction legal-document checklist models, applicability module,
  automatic sanction-completion orchestration, and source §27.1 GET projection.
- Keep the existing pre-sanction application-intake checklist contract working on the shared URL;
  approved applications resolve to the legal checklist and pre-sanction applications retain the
  005D derived intake response. Do not expose a legal refresh/update/approval route.
- Keep checklist ownership in `legal_documents`; preserve the foundation `documents` boundary and
  consume generated-document ids only through a metadata selector.
- Use the source-backed frozen approval review package for shareholding and subsidiary-route facts,
  and persisted application-linked cancelled-cheque metadata for signature mismatch. Missing or
  conflicting shareholding mode produces explicit applicability blockers rather than a guess.
- Use a top-level sanction-completion coordinator to call approval finalisation and checklist
  creation in one outer transaction. The `approvals` package must not import `legal_documents`.

## TDD sequence

1. Add focused legal-checklist tests for approved/non-approved creation, exact item order and
   invariants, physical/demat/subsidiary/mismatch/missing/conflicting facts, metadata-only generated
   document links, replay/no-write behavior, rollback, permissions/object scope, and API envelope.
2. Add an orchestration/dependency-direction test proving final HTTP approval creates the checklist
   atomically without an `approvals -> legal_documents` import.
3. Add a PostgreSQL-only five-worker race test for checklist refresh/creation uniqueness.
4. Run the focused tests first and save the failing output under `evidence/terminal-logs/`.
5. Implement models and one migration, selector/module/view routing, and sanction orchestration.
6. Run the focused tests again and save green output, then run Django check, migration sync, full
   backend coverage, and all frontend build/typecheck/lint/test gates.

## Evidence and closeout

- Save focused red/green logs, full gate logs, API response examples, and a concise dependency/
  transaction trace under the run evidence directory.
- Update `docs/working/API_CONTRACTS.md`, the applicable assumption/epic digest, the selected slice
  status, `.ralph/state.json`, `.ralph/progress.md`, `docs/working/HANDOFF.md`, and the run summary,
  changed-files, risk, and review artifacts.
- Review and sharpen the next one or two Not Started slices using only source material already
  opened for this epic; do not change another slice's status.
