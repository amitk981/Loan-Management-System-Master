# Execution Plan

Selected slice: `007J-registers-and-approval-matrix-frontend-wiring`

1. Inspect the existing RegistersHub and SettingsHub compositions, frontend API/auth seams, the
   delivered 007H/007F/007A backend contracts, and the closest existing container/service tests.
2. Add focused frontend tests first for S23/S25 scoped pagination and filters, frozen-field display,
   nondisclosing states, matrix version/proposal behavior, and permission-gated actions. Retain RED
   and GREEN output in `evidence/terminal-logs/`.
3. Implement typed authenticated services and wire only the owned S23, S25, and S71 panels. Reuse
   current table, form, modal, alert, and pagination patterns; do not calculate backend-owned facts
   or infer authority from metadata.
4. Update the contract/prototype ledgers and create deterministic visual/browser acceptance only if
   the slice declares or the existing harness supports it without changing the approved design.
5. Run focused tests during development, then frontend typecheck, lint, test, and build plus the
   repository backend check, migration-sync, and coverage gates with the mandated interpreter.
6. Review the finished diff against the slice and design rules; save self-contained evidence,
   changed-files, risk assessment, review packet, and final summary.
7. Sharpen the next one or two eligible Not Started slices using only source material opened for
   this run, then mark 007J complete and update Ralph state, progress, handoff, and digest.

Scope controls: no backend model/business-rule changes are planned; no export job is implemented;
unrelated register/settings panels retain their later-slice ownership; protected and source files
remain read-only; git add/commit/push are left to the orchestrator.
