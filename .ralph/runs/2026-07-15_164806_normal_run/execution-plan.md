# Execution Plan

Selected slice: CR-006-register-date-time-timezone-determinism

1. Preserve the impact analysis and source traceability for the UTC-storage/Asia-Kolkata-display
   contract.
2. Add public UI regression assertions for both approval-register consumers of the shared
   date-time formatter.
3. Run the focused register test with `TZ=UTC` and save the expected RED failure.
4. Make the minimal formatter change by explicitly selecting `Asia/Kolkata`.
5. Run the focused test with both `TZ=UTC` and `TZ=Asia/Kolkata`, saving GREEN evidence.
6. Run frontend lint, typecheck, tests, and build; run the Ralph-required backend check,
   migration-drift, and coverage gates with the mandated virtualenv interpreter.
7. Review the diff against the slice and source contract, save evidence and run artifacts, then
   update slice status, Ralph state/progress, and handoff.
