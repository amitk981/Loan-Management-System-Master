# Execution Plan

Selected slice: 006H5-app-shell-application-state-authority

## Permission and scope check

- Allowed edits: `sfpcl-lms/src/**`, `docs/working/**`, `docs/slices/**`,
  `.ralph/state.json`, `.ralph/progress.md`, and this run folder.
- Protected and forbidden paths will not be changed.
- Production scope is limited to removing the `App.tsx` mock application authority and making
  its sole affected consumer, `SanctionWorkbench`, render an honest not-wired empty state.
- Sanction API wiring remains owned by 007I. Existing API-backed application/appraisal screens
  keep their independent server-owned state.

## Implementation sequence

1. Add a failing frontend regression that proves `App.tsx` has no `mockData` import or local
   application status mutation chain, and component coverage for the sanction not-wired state.
2. Save the focused failing output under `evidence/terminal-logs/`.
3. Remove the mock seed/state/update chain from `App.tsx`; pass an explicit empty authoritative
   input to `SanctionWorkbench` and reuse its existing empty-card composition with honest copy.
4. Run the focused tests and save green output.
5. Capture self-contained visual evidence for the affected sanction consumer.
6. Run frontend lint, typecheck, tests, and build plus backend check, migration sync, and the full
   coverage gate with the mandated Ralph virtualenv interpreter.
7. Record changed files, risk assessment, review packet, final summary, state/progress/handoff,
   selected-slice completion, and sharpen the next one or two eligible Not Started slices using
   already-opened digest material.
