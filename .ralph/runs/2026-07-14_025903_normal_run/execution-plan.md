# Execution Plan

Selected slice: 007M-exception-supporting-evidence-and-register-closure

1. Add one public API regression at a time for exception enrichment with supporting document ids:
   valid same-application evidence and immutable metadata, exact replay, malformed/duplicate/bounded
   input, changed replay, and nondisclosing category/sensitivity/permission/object-scope denials.
   Save each failing and passing backend run under `evidence/terminal-logs/`.
2. Deepen the documents-owned reference boundary so approvals supplies a typed exception-workflow
   context and receives immutable display metadata without importing or querying `DocumentFile`.
   Persist the ordered frozen projection on the exact Exception Register entry in one migration and
   include association audit/workflow evidence in the existing locked enrichment transaction.
3. Extend the read-only Exception Register response with the frozen supporting metadata and retain
   the existing immutable approval action comment/actor/time projection. Update the durable API
   contract note.
4. Add a frontend behavior test, then extend the existing S25 table composition and typed client
   row to render decision comments/times and supporting metadata with no inferred download action.
   Add the declared Playwright contract and screenshot names using the production app shell.
5. Run focused backend/frontend tests, Django check and migration sync, then all configured backend
   coverage and frontend build/typecheck/lint/test gates. Save logs and browser collection/launch
   evidence without fabricating screenshots if Chromium is sandbox-blocked.
6. Update the Epic 007 digest, selected slice/status, state, progress, handoff, and required Ralph
   run artifacts. Sharpen the next one or two Not Started slices only if they are not already
   concrete, and verify changed-file/line/migration limits before handoff.
