# Review Packet: 2026-07-12_231540_repair

## Result

Ready for independent validation.

## Slice

006Y13-member-mutation-success-interaction-closure

## Demonstrated Failure and Cause

Both trusted runs completed the identity-change POST and server-side canonical GET, but the E2E spec
counted `canonicalReads` as soon as the POST response resolved. The subsequent GET request event had
not yet reached the listener, so both runs deterministically observed five reads instead of six and
stopped before the final two screenshots.

## Repair

The declared production-route spec now establishes an exact seeded-member GET waiter before each
identity request/approval click, awaits a 200 response, and only then asserts the existing six/eight
ledger counts. Exact mutation bodies, separate requester/checker sessions, projected six-field action,
masked rendering, and screenshot names are unchanged.

## Traceability

- The slice says each mutation must produce exactly one canonical member-detail GET; the spec now
  waits for that exact GET and retains cardinality assertions.
- API contracts §6-§8 and §13.2 require canonical backend responses and protected member data; the
  browser contract still asserts HTTP success, exact bodies, and masked readback.
- Functional spec M02-FR-001/M02-FR-012 requires member maintenance plus approved protected identity
  change; the real finance requester and separate manager checker flow remains intact.

## Verification

- PASS: build, typecheck, lint.
- PASS: 202/202 frontend tests on isolated rerun (an initial parallel run hit an unrelated 5-second
  demo-auth timeout under load).
- PASS: 462 backend tests, 8 expected skips, 93% coverage; migration sync clean.
- PASS: Playwright collection finds the one declared test.
- ENVIRONMENT BLOCK: local Chromium Mach-port registration is denied before test execution.

## Recommended Next Action

Run the trusted browser contract twice outside the sandbox and require all five non-empty screenshots
and the exact request ledger before commit/merge.
