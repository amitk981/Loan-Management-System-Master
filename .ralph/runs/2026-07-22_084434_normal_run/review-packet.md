# Review Packet: 2026-07-22_084434_normal_run

## Result
Ready for independent validation

## Slice
010O-header-notification-summary-wiring

## Outcome

- `Header.tsx` now loads the latest four unread notification rows from the existing API and derives
  its numeric badge from backend pagination `total_count`.
- The dropdown renders loading, populated, empty, error, and unauthenticated states without mock
  fallback, marks individual rows read with their exact persisted version, refreshes after success
  and `409 STALE_WRITE`, and routes View all to the existing Notifications Center.
- The final hard-coded header notification rows are removed. A source regression prevents their
  fixture strings or a `mockData` import from returning.
- No API contract extension was required: the existing list pagination is the bounded-summary
  shape and the existing versioned mark-read endpoint remains unchanged.

## Traceability

The source doc says the global-header bell shows pending workflow/compliance alerts and S04 rows
carry title, severity, timestamp, and read state (`docs/source/screen-spec.md` §§5.1, 5.8, S04). The
code now renders those fields only from `GET /api/v1/notifications/`, uses its pagination count for
the badge, and sends the documented version to mark-read. This is verified by
`Header.notifications.test.tsx`, the exact request assertions in `NotificationsCenter.test.tsx`,
and `e2e/header-notifications.e2e.spec.ts`.

## Validation Evidence

- Focused header/notification regressions: 16/16 passed.
- Complete frontend unit suite: 51 files, 411/411 tests passed.
- Frontend typecheck, ESLint, and production build: passed.
- Django system check and migration-sync check: passed using the mandated Ralph interpreter.
- RED/GREEN logs retained individually for populated, loading, empty, error, unauthorized,
  successful mark-read, and stale-write refresh behavior.
- Contract/mock proof: `evidence/notification-contract-proof.md`.
- Browser handoff: exact spec is present, but two local runs encountered a pre-page Chrome SIGABRT;
  see `evidence/browser-acceptance.md` and both run logs. No screenshot was fabricated. Independent
  trusted validation must rerun the exact spec and decide acceptance.

## Substantive Risks or Decisions

- Decision: no new summary endpoint. `read_status=unread&page_size=4` plus pagination `total_count`
  supplies the slice-required summary through the already documented contract.
- Remaining validation risk is browser infrastructure only; product tests and build gates are
  green. The three screenshots must exist after trusted validation before the run is accepted.

## Recommended Next Action
Run independent Ralph validation, including the exact trusted-browser spec twice, and accept only
if it produces the populated, empty, and error screenshots and all authoritative gates remain green.
