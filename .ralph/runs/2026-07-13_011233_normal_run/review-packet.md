# Review Packet: 2026-07-13_011233_normal_run

## Result

Ready for independent Ralph validation.

## Slice

`006Y15-witness-authority-matrix-behavioral-closure`

## Behavioral Change

- A credit manager with witness-update permission requesting a random absent application receives
  the standard `404 NOT_FOUND` envelope and no persisted evidence.
- Existing and random out-of-scope parent identifiers remain indistinguishable `403
  OBJECT_ACCESS_DENIED` responses before child lookup.
- Unknown contact and identity fields each have a directly selectable public projection/PATCH test,
  exact six-field enabled action, authoritative field error, and unchanged full evidence snapshot.

## Traceability

- `auth-permissions.md` §§3-3.1/19 defines global versus object-scoped access; the application
  authority resolver grants the established credit-manager global scope before returning absence.
- `api-contracts.md` §§6-8 requires standard envelopes; the public witness PATCH returns `404
  NOT_FOUND` rather than a server error or alternate shape.
- `codebase-design.md` §§26.1/27.1/42.2 requires interface-level authority tests and centralized
  object access; `test_witness_api` exercises login, GET action projection, PATCH, and persisted
  outcomes without authority mocks.
- `screen-spec.md` S09 identifies witness identity/contact as governed witness facts; both correction
  families reject unknown verification-time fields without evidence.

## Verification

- RED: `evidence/terminal-logs/red-in-scope-missing-parent.txt` and
  `red-unknown-field-matrix.txt`.
- GREEN/focused: matching green logs, `focused-witness-api.txt`, and `dependency-scan.txt`.
- Full gates: frontend lint/typecheck/build and 204 tests; Django check/migration sync; 486 backend
  tests with 8 expected PostgreSQL-only skips; 93% coverage.

## Recommended Next Action

Run independent validation and, if green, let the orchestrator commit/merge this slice. Then execute
006Z7 followed by 006Z8.
