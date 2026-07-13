# Review Packet: 2026-07-13_034816_repair

## Result
Repair candidate complete; independent browser revalidation required

## Slice
006Z10-portal-limit-interaction-and-boundary-proof

## Recommended Next Action
Run the declared Playwright contract twice outside the sandbox and verify all four non-empty
screenshots, then commit only if the complete Ralph validation passes.

## Demonstrated Failure and Fix

Both prior trusted runs reached `completeApplication` and failed because
`getByRole('button', { name: 'Documents' })` matched the shell's `My Documents` action and the
wizard's `Documents` tab. The repair adds `exact: true` at that interaction and changes nothing else.

## Traceability

- The slice requires the real submit/refetch/reload lifecycle, not rendering-only fixtures.
- The existing scenario still completes nominee, document, declaration, review, submit, canonical
  projection refetch, reload, retained date/rule provenance, and the required screenshot.
- The exact-name repair makes that public interaction reachable without changing any business rule.

## Verification

- Playwright collection: 4 tests in the declared spec.
- Frontend: build, typecheck, lint, and 207 Vitest tests pass.
- Backend: Django check and migration sync pass; 500 tests pass (12 expected skips), 93% coverage.
- `git diff --check` passes and no tagged debug instrumentation remains.
- Local Chromium launch is denied by macOS sandbox services before a page is created; no screenshot
  was fabricated.
