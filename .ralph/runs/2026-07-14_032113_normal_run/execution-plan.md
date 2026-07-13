# Execution Plan

Selected slice: `007N-register-matrix-settings-contract-and-browser-closure`

## Scope and contracts

- Extend the existing authenticated frontend transport in `authSession.ts` with a typed paginated
  list result. Migrate `approvalRegistersApi.ts` so it owns only paths, filters, payloads, and DTOs.
- Add display-ready `authority_summary` and `minimum_approver_count` fields to the approval-matrix
  public list projection. Preserve all retained rule/version facts and keep routing logic backend-owned.
- Render those fields verbatim in the approval-matrix settings panel and retain the governed,
  create-only successor proposal flow.
- Restore the pre-007J2 loan-policy card/field composition using existing Settings patterns while
  retaining real API values, manager/read-only authority, draft truth, and inert future panels.
- Make sidebar visibility and direct-route guards consume one page navigation permission manifest;
  keep panel-level canonical permissions authoritative.
- Implement the declared routed Playwright contract and six screenshot names without component-only
  mounting or locally blessed baselines.

## Incremental RED -> GREEN cycles

1. Add one backend API assertion for display-ready matrix authority/count, run it with the mandated
   backend interpreter to capture RED, implement the serializer projection, then capture GREEN.
2. Add one shared-client pagination/auth/error behavior test, capture RED, add typed paginated
   transport support, migrate the feature service, then capture GREEN.
3. Add focused UI/raw-source tests proving server authority text/count are rendered verbatim and
   duplicate transport/calculation is absent; capture RED, remove React calculations, then GREEN.
4. Add navigation-manifest parity coverage, capture RED, move both sidebar and direct guard facts to
   the one manifest, then GREEN.
5. Add Settings tests for the approved card/field composition, reader/manager states, create-only
   successor, and inert future panels; capture RED, restore the composition with existing classes and
   components, then GREEN.
6. Add/adjust the routed Playwright scenario for scoped S23/S25, matrix reader/manager, loan-policy
   reader, and inert panels; collect it locally and leave real Chromium screenshots to the trusted
   two-run orchestrator gate if the sandbox blocks launch.

## Validation and evidence

- Save each RED/GREEN command output under
  `.ralph/runs/2026-07-14_032113_normal_run/evidence/terminal-logs/`.
- Run scoped frontend/backend tests during implementation, then Django check, migration sync, full
  backend coverage, frontend typecheck, lint, tests, and build.
- Save browser collection/launch output honestly; never fabricate screenshots.
- Produce `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Update API contract documentation if the new public fields are not already recorded; update slice,
  state, progress, handoff, digest, and sharpen the next one or two Not Started slices using only
  source material already opened.

## Guardrails

- No changes to protected files or `docs/source/`; no dependency installation; no git add/commit/push.
- Keep within 30 changed files, 2,000 changed lines, four dependencies, and one migration (no model
  change or migration is expected).
