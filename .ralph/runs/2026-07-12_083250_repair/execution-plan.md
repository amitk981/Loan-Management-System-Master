# Execution Plan

Selected slice: 006Y2-member-form-and-witness-capture-ui-wiring

1. Reproduce the failed trusted-browser path with a collectable Playwright contract and correct
   its navigation seam: close the registration form, search the seeded member, and use the
   directory's existing `Profile` action. Preserve five one-line encoded Chromium baselines.
2. Add failing-first mounted-container tests for member create/edit/reverification and application
   witness capture/edit, including exact request bodies, canonical GET refreshes, inline 400
   validation, authoritative 403/409 handling, and resource-action permission gates.
3. Implement member governance forms and witness panels by composing the existing directory,
   profile, and application-detail patterns. Send current optimistic versions, never merge mutation
   responses locally, never retry rejected writes, and keep protected identity values out of
   fixtures/screenshots.
4. Extend only the existing frontend clients/session permission mapping and deterministic isolated
   E2E seed needed by this UI. Record any real contract mismatch and assumptions.
5. Run focused red/green checks, full frontend and backend gates with the mandated Ralph venv,
   collect the browser spec locally where Chromium is unavailable, and save self-contained evidence.
6. Complete the selected slice and Ralph artifacts, sharpen the next two Not Started slices from
   already-opened Epic 004 material, and verify protected paths/diff limits before handoff.
