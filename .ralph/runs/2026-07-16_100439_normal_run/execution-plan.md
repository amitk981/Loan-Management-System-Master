# Execution Plan

Selected slice: `008M4-documentation-workspace-deep-module-and-design-closure`

## Scope and constraints

- Preserve every 008M3 action, download, redaction, multipart, ordering, pagination, error-state,
  and one-refetch behavior while changing only ownership, query cost, transport reuse, and the
  008M2-only facts layout.
- Keep source-owned legal, security, bank, approval, template, and identity rules behind their
  modules. The staff workspace may bind opaque action identities and compose response DTOs only.
- Use the existing prototype queue/card/table vocabulary; add no styling or visual component.
- Do not modify protected files or `docs/source/`; do not create migrations or dependencies.

## Test-first implementation

1. Capture a dependency/query/transport/layout baseline and map the current coordinator imports,
   direct owner-model queries, action-code branches, exception-name handling, identity selection,
   queue/detail query behavior, local frontend fetch implementation, and facts grid.
2. Add focused failing backend tests for:
   - a page-bounded queue selector with exact final-page metadata and a stable query ceiling as
     inaccessible/off-page rows grow;
   - detail-read query bounds;
   - coordinator dependency/AST rules that require owner decision/execute interfaces and forbid
     owner-model queries, action-code request reconstruction, exception-name authority, and
     arbitrary identity `.first()` selection;
   - owner decision/execute parity through the same current locked facts and unchanged opaque action
     denial behavior.
3. Add focused failing frontend source/behavior tests proving documentation uses the shared
   authenticated request/pagination/multipart transport and that the four-column facts grid is gone
   while S26 facts remain visible in the approved queue/card/table composition.
4. Implement the smallest deep seams:
   - a bounded read selector for permission-scoped queue filtering/counting/page ids and lightweight
     rows;
   - narrow owner-issued workspace projection/decision/execute contracts, including an honest
     governed-identity blocker where no configured owner exists;
   - a shallow coordinator that signs opaque identities and composes DTOs without rebuilding owner
     policy or transport requests;
   - shared frontend transport calls and DTO-only mapping;
   - layout restoration using the existing table/queue rows.
5. Run focused red/green backend and frontend tests, dependency/AST guards, query-count evidence,
   Playwright collection, and the full configured Django/frontend gates. If local Chromium cannot
   launch, retain the honest sandbox log and leave screenshot authority to the orchestrator.
6. Review the final diff against the slice and source references; write the dependency map,
   readability/diff report, risk assessment, review packet, changed-files list, final summary, and
   terminal evidence. Update the selected slice, state, progress, handoff, digest, and sharpen the
   next one or two eligible `Not Started` slices using only already-open source material.

## Expected files

- `sfpcl_credit/processes/` coordinator and bounded selector/owner interface modules
- existing legal/security/application/approval/configuration/identity owner modules as narrowly
  required for decision/execute projection seams
- focused backend workspace tests
- `sfpcl-lms/src/services/documentationWorkspaceApi.ts` and its tests
- `sfpcl-lms/src/pages/documentation/DocumentationHub.tsx` and its tests
- the current run folder and Ralph working/state/slice documentation
