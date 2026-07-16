# Execution Plan

Run: `2026-07-16_192241_repair`

Selected slice: `009B3A-sap-model-owner-and-state-migration`

1. Preserve the quarantined 009B3A implementation and reproduce the two independent validation
   signals: the six historical migration-test errors and the frontend TypeScript failure.
2. Minimise the backend signal by comparing the SAP ownership migration test in isolation with the
   three failing migration-test modules together, then inspect the migration graph targets that
   determine historical model state and physical schema.
3. Add or tighten a regression assertion at the migration-test seam before changing the repair,
   retaining red evidence. Fix only the demonstrated state/schema isolation defect; do not move SAP
   policy, change HTTP contracts, or alter physical business tables/data.
4. Re-run the focused backend loop to green, then run the impacted SAP/loan/readiness tests, Django
   check, migration-sync check, state-only SQL proof, and the required PostgreSQL race acceptance.
   Re-run frontend typecheck without changing frontend production code unless the failure reproduces
   from the checked-in project configuration.
5. Save self-contained red/green evidence, changed-files, risk assessment, review packet, and final
   summary. Reconcile Ralph state/progress/handoff and the executed slice status only after the
   repair gates are green. Leave authoritative full coverage and full frontend validation to the
   orchestrator.

## Permission Check

- Allowed edits: `sfpcl_credit/**`, `.ralph/runs/**`, `.ralph/state.json`, `.ralph/progress.md`,
  `docs/working/**`, and `docs/slices/**`.
- Forbidden/protected paths remain untouched, including `scripts/**`, `docs/source/**`, Ralph
  configuration/permissions, decision/high-risk/design rules, repository agent instructions, and
  git metadata.

## Repair Boundaries

- One existing migration maximum; no second migration.
- No data copy, table rename, schema mutation, decryption, re-encryption, or checksum/digest rewrite.
- No frontend feature or visual change.
- No executable SAP policy transfer; that remains owned by 009B3B.
