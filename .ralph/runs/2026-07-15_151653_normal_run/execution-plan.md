# Execution Plan

Selected slice: 008L3-portal-action-and-resubmission-contract-closure

1. Preserve the required source and review facts in the Epic 005/008 digests, then inspect the
   existing portal documentation, deficiency, lifecycle, audit, storage-capability, frontend, and
   trusted-browser interfaces. Make no changes outside the selected slice.
2. TDD tracer bullet: add a public HTTP regression proving the projection and crafted upload share
   one canonical locked action decision, including reconciled-complete and current-evidence cases.
   Save failing and passing output under `evidence/terminal-logs/`.
3. TDD tracer bullet: add the documentation signed-capability matrix (tamper, expiry, replacement,
   action/account/member/application scope) and central audit vocabulary assertions, then replace
   caller-editable expiry authority with the existing document capability interface.
4. TDD tracer bullet: add a public resubmission regression proving the application-owned guard and
   canonical audit/workflow writer own `incomplete_returned -> submitted`, response events describe
   the response aggregate honestly, and concurrent/invalid attempts have zero success evidence;
   implement the narrow lifecycle interface and delegate to it.
5. Add frontend interaction tests first for the approved MP07 modal/drop-zone composition, distinct
   401/403 and validation states, exactly one canonical refetch, retained Complete plus Download,
   and delayed blob URL revocation. Reuse only existing portal markup and styles when implementing.
6. Add the two declared Playwright specs and four exact screenshot paths using real portal login and
   routed API state. Attempt local collection/non-browser feedback only; leave genuine twice-run
   browser execution to the orchestrator if Chromium services are sandbox-blocked.
7. Update the versioned API contract/digests as needed, run focused tests after every red/green
   cycle, then run frontend lint/typecheck/build/all tests and backend check/migration/full coverage
   with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
8. Save API examples, terminal logs, browser-attempt evidence, changed-files, risk assessment,
   review packet, and final summary. Sharpen the next one or two Not Started slices from already
   opened source facts, then mark only 008L3 complete and update progress, state, and handoff.

Permissions checked: intended edits are limited to `sfpcl_credit/**`, `sfpcl-lms/src/**`,
`sfpcl-lms/e2e/**`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`,
and this run folder. These are allowed by `.ralph/permissions.json`; no protected or forbidden path
will be modified. High risk proceeds under the standing approval; the veto list is empty.
