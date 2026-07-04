# Review Packet: 2026-07-04_071340_architecture_review

## Result
Complete — independent architecture review, no production code changed.

## Slice
architecture-review

## Diff window
`git diff ced57b0..HEAD` — the two slices merged since the prior review (`ced57b0`, 2026-07-03 22:45):
- `002E2-frontend-role-bridge-hardening` (`9a9d3bb`)
- `002EX-early-end-to-end-tracer-bullet` (`027b5b0`)

## Findings (plain English)
1. **Medium — The dev "tracer" grabbed a permanent table name it shouldn't.** The throwaway end-to-end tracer (002EX) correctly namespaced its skeleton tables as `tracer_members`, `tracer_loan_applications`, etc., so they will never clash with the real tables later. But it also added a `workflow_events` table using the *global, canonical* name — the exact table that a planned future slice (003B) is supposed to build from the source data model. Left alone, that future slice's database migration would fail because the table already exists. Nothing is broken today; it is a landmine. **Fix:** I rewrote slice 003B so it must reconcile this (move the model into its proper home or rename the tracer's copy) with no collision.
2. **Low — A dead line of display code in the tracer's browser API client.** One status label can only ever be "recorded"; the "pending" alternative can never run. Harmless and dev-only, but the project's own rules forbid dead code. **Fix:** added a cleanup instruction to slice 002EY, which already owns the tracer screen.
3. **Pass — 002E2 fixed the earlier safety bug well.** Backend roles that the prototype doesn't recognise (e.g. IT Head, Management Viewer) now land on a neutral "Staff User" state with zero permissions instead of accidentally inheriting Auditor screens. Real tests prove it.
4. **Pass — 002EX's backend is genuinely well tested.** The full life cycle persists and is audited; every out-of-order attempt, bad amount, missing/expired login, and permission-less user is rejected before any data is written. These are real behaviour tests, not coverage padding.
5. **Pass with known gap — 002EX's frontend "you can't see the tracer" checks are at the data layer, not the screen layer.** That render/screenshot proof is already assigned to slices 002EY and 002F, so no new work was created.

## Doc-fidelity spot check
- `API_CONTRACTS.md` tracer entry matches the implemented endpoints, envelopes, `401`/`403`/`409` behaviour, and audit/workflow writes. Its citation of `data-model.md §26` for `workflow_events` is exactly why Finding 1 matters — the tracer implemented a shape the source model reserves for 003B.
- `ASSUMPTIONS.md` A-010/A-011 correctly record the frontend permission-bridge scope and the tracer-only permission's removal-before-production requirement.
- Functional-spec requirement-ID sweep (M##-FR-###): not due — Epic 002 is not yet complete (002F, 002G, 002H, 002I, 002J, 002K still Not Started), so no full-epic ID reconciliation is owed this review.

## Corrective slices created / sharpened
- `docs/slices/003B-workflow-event-foundation.md` — mandatory tracer `workflow_events` reconciliation + source-schema requirement.
- `docs/slices/002EY-e2e-and-visual-regression-harness.md` — item 16: remove the dead `tracerApi` ternary.
- `docs/slices/002G-admin-user-and-role-management-shell.md` — sharpened next Not Started slice with concrete endpoints, fields, permission gate, session-revocation-on-suspend, and audit rules.

## Recommended Next Action
Proceed with the normal queue (next Not Started slice is 002F). Ensure whoever implements 003B honours the tracer-`workflow_events` reconciliation before running its migration.
