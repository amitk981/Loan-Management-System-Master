# Execution Plan — 006Y8

1. Add one failing backend parity test at a time for contact and identity correction actions, covering permission, application scope, maker-checker, version, immutable evidence, and malformed/unknown payload denials with no history/audit mutation.
2. Introduce an application-owned witness-correction evaluation consumed by both action projection and PATCH, exposing separate contact and protected-identity actions with the exact six §44 fields.
3. Add failing mounted React tests for separate controls, exact PATCH bodies/counts, one canonical collection refetch, server `400`/`403`/`409` behavior, disabled reasons, and zero forbidden mutation calls; minimally adapt the existing Witness panel.
4. Add the declared trusted Playwright specification using real staff login and routed Application Detail, with no route interception or token injection, and write the three required screenshot paths for orchestrator execution.
5. Run scoped red/green checks, browser collection, then all configured frontend/backend gates. Save self-contained evidence and finalize Ralph artifacts, slice status, state, progress, handoff, and the next eligible slice sharpening.

Permissions checked: planned edits are limited to `sfpcl_credit/**`, `sfpcl-lms/src/**`, `sfpcl-lms/e2e/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and `.ralph/runs/**`, all allowed by `.ralph/permissions.json`. No protected or forbidden path will be modified.

## Repair Plan — 2026-07-12_152102_repair

1. Reproduce the trusted-browser declaration failure with the repository's contract validator and
   save its exact output.
2. Change only the `006Y8` trusted-browser declaration syntax: use the required project-relative
   spec path and explicit screenshot basenames, while retaining the scenario prose outside the
   parser-owned section.
3. Re-run the contract validator and Playwright collection, then refresh the required repair
   evidence and handoff artifacts. Leave the quarantined backend/frontend implementation intact for
   full independent revalidation.

Repair permissions checked: the demonstrated fix is limited to `docs/slices/**` and
`.ralph/runs/**`, both allowed by `.ralph/permissions.json`; no protected or forbidden path is in
scope.
