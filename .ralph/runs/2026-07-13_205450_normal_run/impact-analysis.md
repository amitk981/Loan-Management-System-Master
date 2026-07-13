# Impact Analysis

Selected slice: `CR-004-member-governance-container-recurring-ci-timeout`

## Backend impact

No backend model, endpoint, service, migration, or production behavior changes are required. The
mounted frontend journey replaces `fetch` with a Vitest mock and asserts calls to the existing
member collection/detail contract; it never starts Django.

Grep evidence collected before edits:

- `sfpcl_credit/config/urls.py:333-347` maps the existing member collection, identity-change, and
  detail endpoints.
- `sfpcl_credit/tests/test_member_governance_api.py` covers create, update, detail, and identity
  governance at the real Django boundary.
- `sfpcl_credit/tests/test_member_authority_action_matrix.py` covers member permission and object
  scope.
- `rg "MemberGovernanceForm|member governance" sfpcl_credit --glob '*.py'` found no production
  backend import or dependency on the React container.

Because the fix changes only Vitest timing/execution metadata, no backend regression test is added.
The complete backend quality gate remains the regression guard against accidental cross-stack
effects.

## Frontend impact

Directly affected:

- `src/pages/members/MemberGovernanceForm.container.test.tsx`: mounted production-container suite
  containing the exact create-ledger journey that times out on hosted runners.
- `package.json`: test-script surface used to retain a repeatable, single-worker CI-shaped command
  for this integration-style container file.

Production surfaces exercised but not changed:

- `App.tsx`: authenticated App navigation into the member directory and selected profile.
- `pages/members/MemberDirectory.tsx`: registration container and canonical member selection.
- `pages/members/MemberGovernanceForm.tsx`: labeled field entry and POST/PATCH submission.
- `pages/members/MemberProfile.tsx`: canonical detail refetch and mutation-response
  non-disclosure.
- `services/authSession.ts`, `services/memberDirectoryApi.ts`, and `services/memberProfileApi.ts`:
  session and HTTP seams crossed by the mounted journey.

Existing coverage:

- `MemberGovernanceForm.container.test.tsx` asserts authenticated routing, exact create/update
  ledgers, canonical refetch, response non-disclosure, complete member-type bodies, error matrices,
  and cleanup.
- `MemberGovernanceForm.test.tsx`, `MemberDirectory.test.tsx`,
  `MemberProfile.container.test.tsx`, and `MemberProfile.test.tsx` cover the component and adjacent
  containers independently.

Regression coverage added for the affected test module:

- Preserve the exact named mounted create journey unchanged while making the suite's integration
  timeout explicit and local.
- Make suite execution sequential and add a reusable single-worker/file-serial command, so the
  affected contract can be exercised under a CI-contention-shaped process without skipping or
  quarantining any row.
- Save pre-repair RED output under a deliberately constrained default timeout, then GREEN output
  from the same exact journey after the suite-local policy; repeat the mounted file and run it with
  the complete frontend suite.

## Blast radius

The default `npm test` command still discovers every frontend test. No global timeout is raised, so
all other service, component, page, portal, application, credit, and witness tests retain Vitest's
5000 ms default. The new focused command selects only the existing member-governance container file
and cannot alter production bundles. The suite-local sequential flag prevents its own mounted DOM
journeys from overlapping even if a future global configuration enables concurrent tests.

No other production module consumes test-suite metadata or npm scripts. The only repository-wide
effect is an additional deterministic diagnostic command for CI/review.

## Frontend design compliance

There is no UI change: no component markup, styling, colour, typography, spacing, layout, label,
route, role rule, or runtime data flow is modified. `FRONTEND_DESIGN_RULES.md` therefore requires no
prototype inventory, gap report, screenshot, or browser acceptance update.
