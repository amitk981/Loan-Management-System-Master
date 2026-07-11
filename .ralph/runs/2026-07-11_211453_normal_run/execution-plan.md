# Execution Plan

Selected slice: 006H6-workbench-action-projection-and-interaction-proof

1. Establish the backend public seam and parity baseline:
   - inspect the eligibility, loan-limit, appraisal-workflow, and sanction-handoff public modules;
   - add one failing public-interface test proving resource actions are projected by the owning
     module and match the corresponding service acceptance/rejection predicate;
   - save the red result, implement the shared six-field projection behind the business-module
     boundary, and repeat state/role/permission cases incrementally.
2. Remove `_credit_action_snapshot` from the HTTP adapter and return module-owned snapshots
   unchanged, preserving response envelopes and dependency direction.
3. Add a failing Testing Library test around the default `AppraisalWorkbench` container with the
   authenticated HTTP boundary mocked. Prove one action end to end, then incrementally cover all
   specified mutations, exact URLs/bodies, four-read refreshes, disabled/missing actions, field
   projection, 403/validation feedback, role separation, legacy remediation, and one-call 409.
4. Preserve full typed `AvailableAction` objects through the React container and render backend
   disabled reasons without changing the approved page composition or styling.
5. Run focused backend and frontend tests throughout, then the configured lint, typecheck, build,
   frontend suite, backend check, migration-sync, and full coverage suite with the mandated venv.
6. Save self-contained red/green, HTTP, parity, and gate evidence; review the diff against the
   slice and protected-path/diff limits; write changed-files, risk assessment, review packet, and
   final summary; update the selected slice, state, progress, handoff, digest, and sharpen the next
   one or two Not Started slices using only already-open source material.
