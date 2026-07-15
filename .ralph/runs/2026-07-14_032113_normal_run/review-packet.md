# Review Packet: 2026-07-14_032113_normal_run

## Result
Ready for independent validation

## Slice
007N-register-matrix-settings-contract-and-browser-closure

## Recommended Next Action
Run the independent Ralph gates, including the declared browser contract twice, then commit/merge
only if every check passes. The architecture review is due after this fourth corrective slice.

## Scope Delivered

- Shared typed authenticated pagination and request-id/envelope/error ownership for S23/S25/S71.
- Server-projected matrix authority summary/minimum count rendered verbatim by React.
- One navigation permission manifest for Sidebar and direct route guards.
- Approved S70 policy summary/field-card composition with real retained versions, reader/manager
  authority, create-only draft successors, and inert 008A/012EA panels.
- Routed production-shell Playwright contract for all six named screenshots.

## Standards Review

- Frontend feature services now own only DTOs, paths, filters, and payloads; shared machinery owns
  transport as required by codebase-design §23.5.
- React pages do not decide approval authority (§23.3/§28.3). Raw-source tests reject the removed
  Director/cardinality helpers and duplicated bearer/envelope implementation.
- Existing colors, typography, spacing, cards, fields, modal, alert, table, and tab patterns are
  reused. No new styling system or dependency was added.
- Permission navigation remains UX-only. Register, matrix, and policy panels each enforce their
  canonical backend permission and clear prior facts after authority loss.

## Spec Traceability

- Screen S71 says approval rules display required authority and minimum approver count. The API
  serializes `authority_summary`/`minimum_approver_count`; React displays those exact strings/numbers.
  Verified by the backend public-list test and SettingsHub verbatim/raw-source tests.
- API §§6-8 require standard envelopes/errors/pagination. The shared client returns typed items plus
  server pagination, normalizes an omitted page, sends request ids, and preserves auth/error parsing.
  Verified by `authSession.test.ts` and exact feature-service request tests.
- S23/S25 are independent generated registers. Their filter/page calls stay on separate scoped
  endpoints, atomically replace data, and expose no action/download from metadata ids. Verified by
  RegistersHub tests and the routed browser contract.
- S70 and FRONTEND_DESIGN_RULES require policy fields in the approved Settings composition. The
  ten-column table is removed; real current/retained facts render in the prior card/field layout,
  with read-only and complete create-only successor behavior verified by SettingsHub tests.
- The architecture review required one navigation manifest. Both Sidebar items and direct guards
  now resolve the same manifest, verified across the full parity matrix.

## Validation Evidence

- RED/GREEN: `evidence/terminal-logs/backend-matrix-projection-*.txt` and the five frontend
  `*-red.txt` / `*-green.txt` pairs for pagination, transport, matrix rendering, navigation, and
  policy composition.
- Full frontend: build, typecheck, lint, and 257 tests pass (`frontend-*.txt`).
- Full backend: check and migration sync pass; 687 tests pass with 19 expected skips; coverage is
  93% (`backend-*.txt`).
- Browser: `browser-spec-collection.txt` lists the exact declared spec; `browser-local-attempt.txt`
  records ready servers and the expected Chromium Mach-port denial. No PNG was fabricated.
- Diff remains below Ralph limits: 24 status entries, no dependency or migration, and well below
  2,000 changed lines.
