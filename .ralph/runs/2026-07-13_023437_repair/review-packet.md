# Review Packet

## Outcome

The trusted-browser portal entry now waits on a complete, renderable dashboard and activates the
real dashboard `New Loan Application` control. The previous fixture omitted required member fields;
when its request resolved, MP03 threw and removed the very control Playwright was trying to use.

## Repair Scope

- Added a complete `PortalDashboard` fixture guarded with TypeScript `satisfies`.
- Replaced the remount-prone sidebar/native-click workaround with the dashboard action and ordinary
  Playwright click after that action becomes visible.
- Added a focused raw-contract regression requiring the render-critical fixture fields and exact
  dashboard action.
- Preserved all existing limit response, request, redaction, advisory, review, and screenshot checks.
- Changed no production code in this repair.

## Traceability

The slice requires mounting the routed real portal container and proving server-only limit states.
The browser spec still enters through real member login and mounts MP05; the complete typed dashboard
fixture prevents a test-only render failure before that boundary. The four declared Playwright cases
continue to verify available, unavailable, over-limit advisory, and review-maximum states.

## Verification

- Focused regression: red on missing `member_type`; green with 5/5 tests.
- Playwright collection: 4/4 declared cases collected.
- Frontend: typecheck, lint, 205 tests, and production build pass.
- Backend: Django check and migration sync pass; 494 tests pass with 12 expected PostgreSQL-only
  skips; coverage is 93% (floor 85%).
- Local Playwright execution reaches browser launch but is denied by the documented macOS Mach-port
  sandbox restriction. No screenshots were fabricated; independent validation owns both trusted runs.
