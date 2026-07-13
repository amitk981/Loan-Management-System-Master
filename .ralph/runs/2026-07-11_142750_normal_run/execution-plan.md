# Execution Plan

Selected slice: `005FA3-portal-auth-interaction-and-demo-flag-proof`

1. Preserve the 005FA2 production behavior and approved visual composition; expose only the
   minimum app boundary needed for interaction tests if the real boundary cannot otherwise be
   mounted deterministically.
2. Replace the portal login raw-source assertions with rendered DOM tests for empty and populated
   submissions, including exact callback counts and credential payloads.
3. Add module-isolated app/session tests for false/unset and true `VITE_ENABLE_DEMO_AUTH` states.
   Prove pre-login denial, the approved staff-only demo surface when enabled, real backend-session
   installation, and unconditional local identity/permission clearing after failed network logout.
4. Run the new tests red first and save the failing output, implement only defects/test seams
   exposed by that run, then save focused green output.
5. Add a browser interaction proof for the corrected portal-login validation state and save a
   self-contained screenshot where the sandbox permits browser launch.
6. Run frontend lint, typecheck, tests, and build plus the configured backend check, migration
   sync, full tests, and coverage gate. Save all outputs and required Ralph review artifacts.
7. Mark 005FA3 complete; update progress/state/handoff and sharpen the next one or two Not Started
   slices using only the already-opened Epic 005 digest or other source material opened in this run.

Risk controls: no credential bypass, permission grant, production styling, backend/API contract,
or source/protected-file change is authorized. Demo behavior remains gated by the existing build
flag, and logout failure must fail closed locally.
