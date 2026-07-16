# Execution Plan

Selected slice: 009B3A-sap-model-owner-and-state-migration

1. Reproduce the prior independent failure with the smallest deterministic migration-test
   sequence that leaves `sap_customer_codes` absent before the SAP owner-transfer fixture is
   created; preserve the prior run's traceback as the initial red evidence.
2. Rank and test schema-state isolation hypotheses without changing the production ownership
   migration or any executable SAP policy.
3. Add or tighten only the migration-test regression seam that caused the demonstrated full-suite
   order dependency, then run the focused red/green sequence with the mandated backend interpreter.
4. Run the impacted SAP ownership tests, historical migration-order tests, Django check, and
   migration-sync gate; leave authoritative full-suite coverage to the orchestrator.
5. Save repair evidence and required Ralph artifacts, audit the diff against permissions and the
   slice boundary, and update run/state/handoff records without committing or pushing.

## Permission Check

- Repair edit permitted: `sfpcl_credit/tests/test_legal_document_boundary.py` is covered by
  `sfpcl_credit/**` in `.ralph/permissions.json`.
- Evidence/bookkeeping edits permitted: `.ralph/runs/**`, `.ralph/state.json`,
  `.ralph/progress.md`, and `docs/working/**`.
- Protected/forbidden paths remain untouched, including scripts, Ralph configuration/permissions,
  agent instructions, decision/high-risk/design rules, git metadata, and `docs/source/**`.

## Repair Boundary

- Preserve the existing uncommitted 009B3A implementation.
- Change only the demonstrated historical migration-test isolation failure.
- Do not alter production SAP model state, executable policy, schema/data operations, API behavior,
  frontend behavior, or the already-sharpened 009B3B/009D2 requirements.
