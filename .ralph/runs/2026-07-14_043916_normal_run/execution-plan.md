# Execution Plan

Selected slice: 007P-sanction-queue-pagination-and-read-boundary-closure

## Scope and interface seams

- Deepen the shared authenticated list interface so a successful collection is accepted only when
  `data` is an array and the complete API-contract pagination object is non-negative and internally
  coherent. Preserve existing authentication and error-envelope behavior.
- Change the sanction feature interface to return `{ items, pagination }`, with explicit `page` and
  `page_size` plus the exact sanction/status/assignment filters on every request.
- Reuse the existing S21 workbench and pagination-button patterns. Display the server total, replace
  rows and pagination together after every request, and clear both on access/error/malformed results.
- Keep selector work as coarse actor/type/status/assignment query shaping. Validate supported filter
  values up front, then pass every candidate through the canonical
  `approval_case_is_readable(actor, case)` interface before counting, paging, or serializing.

## TDD tracer bullets

1. Frontend shared transport RED/GREEN: add one malformed-envelope behavior at a time (non-array
   data; missing, malformed, negative, and inconsistent pagination), preserving valid/auth/error
   behavior after each cycle.
2. S21 RED/GREEN: prove exact first-page filters and server total, next-page navigation, status
   filter reset, empty/access/error replacement, and malformed-response error rendering through the
   public rendered page and shared HTTP seam.
3. Backend RED/GREEN: reject unknown `approval_type` and `current_status`; construct cross-page
   relevant/noncandidate/malformed cases, instrument the canonical readable interface, and prove
   coarse narrowing plus hole-free canonical totals/pages without SQL-text or query-count assertions.
4. Trusted-browser contract: extend the declared S21 scenario with a deterministic multi-page list
   envelope, exact retained query parameters, page/filter interaction, malformed envelope error,
   and the required `sanction-paginated-filtered-queue.png` screenshot declaration. Locally collect
   the Playwright spec; leave actual Chromium evidence to the orchestrator if sandbox services deny
   launch.

## Verification and completion

- Save focused frontend/backend RED and GREEN logs plus validator-call measurements under
  `evidence/terminal-logs/`.
- Run frontend build, typecheck, lint, and tests; backend check, migration sync, and the full coverage
  suite using `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Review the diff against the slice/source contracts and protected-path/diff limits; save changed
  files, risk assessment, review packet, and final summary.
- Mark only 007P complete; update state, progress, handoff, API contract notes if the public client
  contract warrants it, and sharpen the next one or two Not Started slices using already-opened
  Epic 007 material while preserving their status.
