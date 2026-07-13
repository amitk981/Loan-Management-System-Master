# Impact Analysis — CR-002

## Backend

No backend model, endpoint, service, or test is affected. Repository search for
`MemberGovernanceForm` and the failing test title finds only frontend TypeScript/TSX files; the
test's HTTP boundary is a local `fetch` stub and no Django code executes.

## Frontend

- Directly affected: `src/pages/members/MemberGovernanceForm.container.test.tsx`, specifically its
  mounted `App` create/read/update/read journey and shared complete-form fixture entry helper.
- Production surfaces exercised but not changed: `App`, `MemberDirectory`,
  `MemberGovernanceForm`, and `MemberProfile`, including the `/members` route and member HTTP
  client boundary.
- Other consumers in the blast radius: the three parameterized complete-body container journeys
  use the same fixture-entry helper; the remaining identity and error-matrix tests share the same
  file-level DOM and global-fetch cleanup.

## Regression Coverage

- Preserve the existing exact create body, canonical create readback, exact ordinary PATCH body,
  canonical update readback, navigation, and mutation-leak assertions in the routed journey.
- Add a focused regression assertion that bulk fixture entry avoids per-character keyboard work
  while still dispatching observable input/change behavior through the mounted public form.
- Exercise the routed journey repeatedly and run the following parameterized test in the same
  focused command to detect leaked DOM or asynchronous work.
- Existing `MemberGovernanceForm.test.tsx` remains the component-level production-form regression
  suite; no separate module requires a new test because production code and public behavior are
  unchanged.

## UI and Design Compliance

No UI or production styling change is planned. The approved frontend composition, labels,
layout, colors, typography, and actions remain untouched, so `FRONTEND_DESIGN_RULES.md` is
preserved.

## Risk / Blast Radius

The change is confined to test fixture interaction and cleanup. The main risk is making entry
faster by bypassing the browser-observable input contract; regression assertions must therefore
continue to drive labeled controls and verify the exact public HTTP requests and canonical UI
readbacks. A second risk is incomplete teardown after a timed-out assertion; cleanup must be
registered before tests run and avoid pending per-character user-event work.
