# Impact Analysis

## Change Boundary

This change request repairs timing nondeterminism in
`sfpcl-lms/src/pages/members/MemberGovernanceForm.container.test.tsx`. It changes test structure
only. No production UI, API contract, backend behavior, styling, route, package, or workflow is in
scope.

## Backend Models, Endpoints, and Services

- A repository search for `MemberGovernanceForm` finds no backend references; the component is a
  frontend-only container.
- The mounted journey observes the existing member endpoints without changing them:
  `GET/POST /api/v1/members/` and `GET/PATCH /api/v1/members/{member_id}/`.
- The existing identity-change cases also observe
  `POST /api/v1/members/{member_id}/identity-change-requests/`.
- No backend model, serializer, view, service, migration, or endpoint contract is affected.
- Backend regression tests to add: none, because no backend module or behavior changes. The full
  backend check, migration-sync check, and coverage suite remain regression gates.

## Frontend Screens, Components, and Routes

- Directly edited: `MemberGovernanceForm.container.test.tsx`.
- Exercised production components: `App`, `MemberDirectory`, `MemberGovernanceForm`, and
  `MemberProfile`.
- Exercised route journey: authenticated application shell -> Members & Borrowers -> Register
  Member -> canonical member profile -> ordinary update -> canonical member profile.
- Production regression tests to add/change: split the oversized routed journey into focused
  mounted tests that collectively retain registration/navigation, exact POST body, canonical create
  readback, ordinary human-like update, exact PATCH body, canonical update readback, and cleanup.
  Keep the immediately following complete-body parameterized case in the stress execution.

## Blast Radius and Other Consumers

- `MemberDirectory` consumes `MemberGovernanceForm` for create and selects the returned member id.
- `MemberProfile` consumes `MemberGovernanceForm` for ordinary updates and refreshes the canonical
  profile after save.
- `App` owns authentication, navigation, and the directory/profile route state used by the mounted
  journey.
- `MemberGovernanceForm.test.tsx` covers the form directly, including complete create, update,
  identity change, errors, and masked-value behavior. It is not edited; the complete frontend suite
  remains its regression gate.
- No other module imports the container test or test helpers, so no other affected module requires a
  new dedicated regression test.

## Frontend Design Rules

There is no UI or production-code change. The approved component composition, styles, colours,
typography, layout, labels, and behavior remain untouched. The refactored tests continue to mount
the existing production containers and interact through labeled controls.

## Regression Evidence Plan

- RED-capable baseline: repeat the exact oversized routed test under a deliberately constrained
  per-test timeout and save the output, demonstrating that runner speed can make the monolithic
  journey fail without changing assertions.
- GREEN: run the refactored focused tests at least 20 consecutive times together with the immediately
  following complete-body parameterized case.
- Run frontend typecheck, lint, full tests, and build; run backend check, migration sync, and full
  coverage using the mandated Ralph virtualenv interpreter.
