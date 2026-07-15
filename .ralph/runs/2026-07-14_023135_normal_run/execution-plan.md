# Execution Plan

Selected slice: `007L-sanction-workbench-contract-and-browser-closure`

## Scope and permissions

- Change only the approval-case frozen read projection, shared frontend transport, sanction feature
  service/page/tests, the declared sanction Playwright contract, and Ralph evidence/state documents.
- Allowed edit roots were checked against `.ralph/permissions.json`: `sfpcl_credit/**`,
  `sfpcl-lms/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and
  `.ralph/runs/**` are permitted.
- Keep `docs/source/**`, scripts, Ralph configuration/permissions, repository agent instructions,
  decision/high-risk/frontend policy files, and Git metadata unchanged.

## Public interfaces and behavior

1. Extend the approval module's canonical case projection with the complete S21 frozen row facts,
   including an honestly labelled elapsed pending-age display fact derived from the frozen submitted
   timestamp. Preserve the existing actor-scoped ordering, count, pagination, and canonical
   validity checks; do not query live appraisal/configuration rows per case.
2. Deepen the shared frontend request seam so both JSON and multipart requests share session,
   authorization, envelope parsing, and error normalization. Keep sanction feature code limited to
   typed paths, query parameters, payloads, and multipart field construction.
3. Make every sanction collection request explicitly include `approval_type=sanction`; pending also
   includes `current_status=pending&assigned_to_me=true`. Render all S21 row facts and immutable S22
   action comments/roles/times without client-owned authority or TAT policy calculations.
4. Require three new accepted legal uploads whenever changed General Meeting evidence is recorded.
   Do not reuse or describe case metadata ids as referenceable, and do not expose recording without
   both the enabled resource action and required `/auth/me` permissions.
5. Preserve the existing single decision modal, exact action paths/bodies, mandatory comments,
   stale/conflict/meeting error precedence, one-call stale behavior, canonical refetch, independent
   sanction-decision permission, and returned-cycle isolation.
6. Tighten `e2e/sanction-workbench.e2e.spec.ts` to assert exact routed collection contracts and
   exercise the real app shell across the seven declared deterministic screenshots.

## Test-first sequence

1. RED/GREEN: backend public collection/detail tests for the complete frozen queue projection,
   immutable action evidence, honest pending elapsed display, and no live per-row reconstruction.
2. RED/GREEN: frontend transport tests for authenticated multipart success and normalized failures;
   move upload mechanics behind that seam.
3. RED/GREEN: sanction service/container tests for exact query strings, queue/detail rendering,
   action permission intersections, canonical refresh/error behavior, and mandatory fresh evidence.
4. Collect the named Playwright spec locally. If Chromium is blocked by the sandbox, retain the
   collection result and leave screenshot adjudication to the orchestrator's two trusted runs.

## Verification and closeout

- Run focused backend tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, focused frontend
  tests, then backend check/migration sync/full coverage and frontend build/typecheck/lint/full tests.
- Save red/green and gate outputs under `evidence/terminal-logs/`; do not fabricate browser images.
- Review the diff for source fidelity, scope, protected paths, mock ratchet, and diff limits.
- Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update the
  Epic 007 digest, assumptions only if needed, handoff, progress, state, and this slice status.
- Sharpen the next one or two `Not Started` slices only if the already-open Epic 007 sources add
  concrete requirements not already present.
