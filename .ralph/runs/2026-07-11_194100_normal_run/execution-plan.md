# Execution Plan

Selected slice: `005E3-completeness-authority-fidelity-and-interaction-closure`

## Boundaries and permissions

- Work only in the active Ralph worktree and this run folder.
- Edit only permitted application/frontend tests and code, working documentation, the selected
  slice, the next one or two eligible slice files, `.ralph/state.json`, and `.ralph/progress.md`.
- Do not edit protected paths or `docs/source/`; the selected slice is approved under the owner's
  standing high-risk policy and is not revoked.
- Keep the change within the 30-file/2,000-line/one-migration limits; no dependency or schema change
  is expected.

## Public behaviors to prove (incremental red/green)

1. Backend completeness and deficiency reads expose §44-shaped resource actions whose enabled
   state and disabled reason are produced by the same application-module validators used by pass,
   return, resolve, and rejection-note writes. Prove permission, object scope, application state,
   blockers, open deficiencies, duplicate rejection note, and reference/register boundaries via
   public API calls, including denied calls with no writes.
2. Frontend detail loading consumes both completeness and document-checklist projections, joins
   rows by document type, and fails closed on disagreement while retaining canonical application,
   nominee, deficiency history, and reference facts.
3. The real `CompletenessWorkbench` container preserves full resource action objects, intersects
   them with `/auth/me` only for usability, hides absent actions, explains disabled actions, and
   performs pass/return/resolve/reject with exact URLs and bodies followed by canonical queue,
   completeness, document-checklist, and deficiency refreshes.
4. Validation, 401/403, and 409 are visible through existing patterns. A 409 sends one mutation,
   never retries automatically, and refreshes canonical state only after the user chooses Refresh.
5. Restore the approved pre-005E2 S12 category/item/document-chip hierarchy and action placement
   using existing styles/components only, with no mock facts or frontend-owned workflow decisions.

## Implementation and verification sequence

1. Add one focused backend API/action-parity test and save its failing output, implement the
   applications-module action projection and view reuse, then save green output. Repeat for the
   remaining authority boundaries without batching speculative tests.
2. Add one real-container frontend test for the dual checklist read and mutation refresh contract,
   save red output, implement the smallest service/container changes, and save green output. Add
   denial, validation, stale, and mismatch cases incrementally.
3. Restore the prior S12 composition from repository history while retaining only canonical API
   data and authoritative resource actions; update focused rendering tests.
4. Run focused backend and frontend suites, then backend check/migration sync/full coverage and
   frontend lint/typecheck/tests/build with the mandated backend interpreter.
5. Run the pinned Playwright acceptance path where available and save deterministic screenshots
   plus a self-contained fidelity checklist/API examples in this run folder.
6. Audit the final diff for protected paths and limits; write changed-files, risk assessment,
   review packet, and final summary. Update the selected slice to Complete, state/progress/handoff,
   assumptions/API-contract documentation if affected, and sharpen the next one or two Not Started
   slices from already-opened digests.
