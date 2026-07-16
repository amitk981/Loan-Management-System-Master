# Execution Plan

Selected slice: 009B3C-sap-current-evidence-and-adapter-contract-closure

1. Reproduce the independent full-suite failure with the single named readiness test using the
   orchestrator-managed backend interpreter, and retain the failing output as repair evidence.
2. Compare the failing fixture's SAP send/completion ledgers with 009B3C's current-evidence
   contract and rank falsifiable causes without broadening the slice or weakening reconciliation.
3. Add or refine the narrowest regression fixture/test needed to express the intended exact SAP
   tuple, confirm the red signal, and make only the demonstrated compatibility repair.
4. Run the focused readiness regression and impacted SAP adapter/current-evidence tests green;
   run backend check and migration-sync, leaving the complete backend suite to independent Ralph
   validation as required.
5. Save red/green logs and repair artifacts, verify no protected files or debug instrumentation
   changed, update handoff/progress/state only if repair truth differs, and delegate all git work
   to the orchestrator.
