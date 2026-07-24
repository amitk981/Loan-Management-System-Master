# Execution Plan

Selected slice: 011PA-default-case-notes-frontend-wiring

## Scope

Wire only the S53-S55 read side of the existing Default/Recovery Hub to the backend contracts
delivered by 011A-011D. Preserve the prototype visual system, remove S53-S55 business fixtures,
and keep S56/S57 recovery decisions and execution unavailable until 011PB.

## Permissions and boundaries

- Product edits are limited to allowed `sfpcl-lms/` paths and current-run evidence under
  `.ralph/runs/2026-07-24_211119_normal_run/`.
- Do not modify protected workflow files, `docs/source/`, mechanical Ralph state/progress/handoff,
  or the selected slice status.
- Do not add dependencies, backend models, API behavior, or recovery mutation controls.
- Stay below 30 changed files and 2,000 changed lines.

## Implementation sequence

1. Read the binding frontend design rules and inspect the existing Default Hub, Epic 011 service
   seam, route/auth patterns, focused tests, and trusted-browser examples.
2. Add focused failing request/render tests for list/detail reads, grace/extension/frozen-note
   projections, loading/empty/error/unauthorized/blocked states, and unavailable recovery actions.
   Save RED output under `evidence/terminal-logs/`.
3. Minimally extend the shared Epic 011 API seam and wire the page container to authoritative
   server projections. Remove S53-S55 inline/mock business fixtures without touching the 011PB
   decision/execution ownership boundary.
4. Make focused tests green and save GREEN output. Run reverse-consumer tests plus frontend
   typecheck, lint, and build.
5. Implement the exact trusted-browser spec
   `e2e/default-closure-compliance-staff.e2e.spec.ts`, run it twice, and save
   `default-case-workbench.png` from each passing contract run in current-run evidence.
6. Inspect diff stats and targeted hunks for scope, mock removal, authority, permission states, and
   protected-path compliance.
7. Complete self-contained evidence, `risk-assessment.md`, `review-packet.md`, and
   `final-summary.md`; set the review result exactly to `Ready for independent validation`.

## Validation commands

- Focused Vitest files for the Epic 011 API seam and Default Hub.
- Focused reverse-consumer Vitest files affected by the shared seam.
- `npm run typecheck`
- `npm run lint`
- `npm run build`
- Exact Playwright trusted-browser spec twice, without fabricating screenshots.

The orchestrator owns authoritative full/impacted backend validation and all commit, merge, state,
status, changed-file, and handoff bookkeeping.
