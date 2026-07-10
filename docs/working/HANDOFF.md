# Ralph Handoff

## Last Run
2026-07-10_235256_normal_run

## Current Status

004E now captures witnesses only under real loan applications and verifies them from persisted
member, KYC, and shareholding facts.

- `GET/POST /api/v1/loan-applications/{id}/witnesses/` uses standard envelopes, narrow witness
  read/create permissions, and application object access.
- A verified witness must name-match a real member, have verified KYC, and hold active positive
  shares. Caller-supplied verification facts are rejected.
- PAN/Aadhaar use the shared protected-identity seam, remain masked in responses, and are absent
  from metadata-only audit evidence. Creation writes no workflow event or application transition.
- The source catalogue/path gap and conservative active-positive shareholder rule are recorded in
  A-062. No frontend or documentation-stage completion behavior was introduced.

## Validation

All configured gates passed: Django check, migration sync, 384 backend tests with expected
PostgreSQL-only skips, 94% coverage (85% floor), frontend lint/typecheck, 126 tests, and build.
Focused red/green, API examples, and gate logs are under
`.ralph/runs/2026-07-10_235256_normal_run/`.

## Next Run

Run `006G2-sanction-handoff-module-and-read-contract`, retaining the exact 006F4 PostgreSQL command
after the approvals-module extraction. Then run 006H2 and 006H3 before the `006X` two-role tracer.
