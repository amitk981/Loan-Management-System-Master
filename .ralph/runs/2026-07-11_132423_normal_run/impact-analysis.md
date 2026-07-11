# Impact Analysis

## Affected backend

No backend model, endpoint, service, or production command changes are required. Grep of the named
screenshots, clock rendering, `toHaveScreenshot`, `E2E_DJANGO_PYTHON`, and Playwright timezone
configuration found the defect entirely in `sfpcl-lms/`. The existing Playwright web server will
continue to exercise the real login, current-user, dashboard-summary, and tracer endpoints without
changing their contracts or implementation.

## Affected frontend and harness

- `src/pages/Dashboard.tsx` consumes the browser clock for its greeting and date, but production
  code must remain unchanged.
- `e2e/tracer.e2e.spec.ts` owns the tracer-user dashboard screenshot.
- `e2e/auth-negative.e2e.spec.ts` owns the zero-permission dashboard screenshot.
- `e2e/helpers.ts` is the shared seam for a dashboard-only browser clock fixture.
- `playwright.config.ts` owns browser context settings and must explicitly select `Asia/Kolkata`.
- `e2e/README.md` owns the normal and snapshot-update operator commands.

The existing app route is the staff `dashboard` route rendered by `App.tsx` inside `AppShell`.
No route or component API changes are needed.

## Blast radius and other consumers

- The fixed browser clock affects only the two dashboard screenshot scenarios that opt into the
  helper. Login, tracer closed-state, application-detail, and member-portal E2E scenarios retain
  the real clock.
- The project-level timezone setting affects all Playwright browser contexts, stabilising locale
  rendering to the product timezone without changing application code or backend processes.
- `staffLogin` remains unchanged and is consumed by the tracer, zero-permission, and other staff
  authentication scenarios.
- The README interpreter expression is operator documentation only. It resolves the one shared
  Ralph virtualenv from Git's common directory in both a primary checkout and a Ralph worktree.

## Existing and new regression coverage

Existing coverage is the full-page `dashboard.png` assertion in `tracer.e2e.spec.ts` and
`dashboard-zero-permission.png` in `auth-negative.e2e.spec.ts`; `Dashboard.test.tsx` covers the
summary presentation but not the browser clock.

Regression coverage to add:

- Shared E2E helper: install a fixed instant before page application code executes.
- Tracer module: assert `Good afternoon, E2E` and the exact seeded-role header
  `SFPCL LMS · E2E Tracer Staff · Friday 10 July, 2026` before the screenshot.
- Auth-negative module: assert the same greeting and the exact seeded-role header
  `SFPCL LMS · IT Head · Friday 10 July, 2026` before the screenshot.
- Playwright config: explicitly set `timezoneId: 'Asia/Kolkata'`; validate via both repeated
  screenshot scenarios without snapshot updates.
- README: exercise both documented shell expressions from this worktree and verify the resulting
  path equals the shared Ralph interpreter.

## Frontend design compliance

There is no product UI change: no colours, typography, spacing, layout, component, label, or
production date/greeting behaviour changes. The correction is isolated to the test harness and
operator documentation, so `FRONTEND_DESIGN_RULES.md` remains fully satisfied.
