# Execution Plan

Selected slice: `008L4-portal-production-boundary-and-browser-proof`

## Scope and seams

- Keep `sfpcl_credit.processes.portal_documentation_actions` as the one deep module interface for
  portal documentation GET, upload, and issued-document download. Make its authority decision lock
  the canonical application/checklist/current item and consume 008K5 borrower-safe completion truth
  for both reads and writes.
- Resolve published Term Sheet and Loan Agreement content from the current legal-document renderer
  selector under the same application lock. Do not trust or mutate a checklist item's retained
  pointer to choose current content.
- Route portal upload and download evidence through the central document audit writer with exactly
  `portal.document.uploaded` / `portal.document.downloaded` and safe source-required metadata.
- Keep `portal_deficiency_response` and the existing application lifecycle owner as the response and
  resubmission seams; align the immutable response projection with retained workflow state while the
  staff deficiency remains open.
- Preserve the existing MP07/MP11/MP13 React composition. Replace only the two declared Playwright
  specs' catch-all API interception with real Django fixtures/login/API calls and genuine production
  responses; mock no internal backend behavior.

## TDD tracer bullets

1. RED: add a public-process/API test proving GET and POST use one locked current action decision,
   including completion-versus-upload zero-write loser evidence. GREEN: introduce the shared locked
   decision implementation and route projection/upload through it.
2. RED: add generation-successor tests proving production generation immediately changes projection,
   invalidates the old signed capability, and serves the new current renderer without direct checklist
   FK assignment. GREEN: resolve current documents through the legal-document owner under lock.
3. RED: add upload/download tests requiring exactly one source audit action with complete safe facts,
   and none for tamper, expiry, replacement, or cross-scope denials. GREEN: extend/reuse the central
   document audit writer and remove generic/parallel event writes.
4. RED: add deficiency upload/re-upload/resubmit/replay tests requiring projection and retained
   workflow state to agree on `responded` versus `submitted_for_review`. GREEN: correct the response
   state serialization/evidence without resolving the staff-owned deficiency or rewriting history.
5. RED: convert the declared Playwright specs to fail collection/static boundary checks if they use
   catch-all `/api/v1/**` routing, then implement real server fixture setup, login, upload/refetch,
   signed download/tamper/crafted denial, lifecycle guard, and resubmission flows. Preserve the four
   declared screenshots and desktop/mobile viewports.

## Verification and evidence

- Save every focused failing-first and passing run in
  `.ralph/runs/2026-07-15_193120_normal_run/evidence/terminal-logs/`.
- Run focused backend and frontend tests regularly, Playwright collection, Django check and migration
  drift, then the full configured backend coverage and frontend lint/typecheck/test/build gates.
- Attempt local browser execution only if Chromium launches; never fabricate screenshots. Retain the
  exact trusted-browser contract for the orchestrator's twice-run localhost acceptance.
- Update API contracts if the portal response/audit contract changes, then complete risk assessment,
  review packet, changed-files list, final summary, state/progress/handoff, selected slice status, and
  sharpen the next one or two Not Started slices using only source material already opened.

## Constraints

- No protected/source file edits, dependency installs, git staging/commit/push, new styling, direct
  lifecycle status assignment, synthetic business rules, or changes outside this vertical slice.
