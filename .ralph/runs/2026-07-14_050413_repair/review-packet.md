# Review Packet: 2026-07-14_050413_repair

## Result
Ready for independent validation

## Slice
007P-sanction-queue-pagination-and-read-boundary-closure

## Demonstrated Failure and Repair

Both trusted runs failed because the malformed-response phase selected the `approved` filter while
the mock route inferred expected query parameters from response mode `malformed` and asserted that
no status existed. The assertion threw before `route.fulfill`, allowing a real unauthenticated
request and cascading into the missing malformed-pagination error.

The repair maps response mode `malformed` to the expected selected query status `approved`. It does
not weaken the contract: `approval_type=sanction`, explicit page/page size, no assignment filter,
and the malformed successful envelope are still asserted/exercised.

## Traceability

- The slice/source contract requires historical S21 filters on every page and malformed paginated
  success to render as error (`screen-spec.md` S21; `api-contracts.md` §§6.2 and 8.1).
- The browser spec now expects the exact `approved` status chosen for the malformed-response request,
  then returns a success envelope without pagination.
- Production strict-envelope behavior remains covered by `authSession.test.ts`, and S21 pagination/
  replacement behavior remains covered by `SanctionWorkbench.test.tsx`.

## Verification

- PASS: Playwright lists the declared Chromium test.
- PASS: frontend build, typecheck, ESLint, and 269 Vitest tests.
- PASS: Django check and migration sync.
- PASS: 692 backend tests, 19 expected PostgreSQL-only skips, 93% coverage (85% floor).
- ENVIRONMENT LIMIT: local Chromium launch denied by macOS Mach-port sandbox before test execution.
- PENDING INDEPENDENT GATE: both trusted browser runs and screenshot acceptance.

## Recommended Next Action
Run full independent validation, including both declared trusted browser executions. Commit/merge
only if both pass; otherwise keep the worktree quarantined with the new exact failure summary.
