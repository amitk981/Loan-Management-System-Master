# Slice 005FA4: Portal Auth Real-Boundary Flag Proof

## Status
Not Started

## Parent Epic
Epic 005: Application Intake and Completeness
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal

Finish 005FA3's promised proof by exercising false, unset, and true demo flags through the real
App/RoleProvider boundary, with no manually projected LoginScreen props and no unexecuted browser
contract accepted as evidence.

## Depends On
- 005FA3

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/auth-permissions.md` authentication, session, and frontend guard sections
- `docs/source/security-privacy.md` session revocation/logout controls
- `docs/source/codebase-design.md` §23.3 and §26.3
- `docs/slices/005FA3-portal-auth-interaction-and-demo-flag-proof.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-11_191720_architecture_review`

## Scope

- Replace the static `LoginScreen` flag projection with real App/RoleProvider boundary tests in
  separately reset module/build environments for unset, explicit false, and true.
- Unset/false must expose neither staff demo role selector nor demo continuation, and must expose no
  protected staff/member content, roles, permissions, or actions before backend session restore.
- True may expose only the already-approved staff demo controls. It must not create any portal
  credential bypass, borrower identity, portal permission/action, or protected portal route.
- Exercise the real portal form's empty and populated submissions and failed-network logout through
  the same boundary. Assert exactly one real login request and that logout clears stored tokens,
  identity, roles, role codes, permissions, actions, member/portal claims, and protected content.
- Keep production behavior and visual composition unchanged unless a failing boundary test exposes
  a real defect.

## Test Cases

- Module-isolated real-boundary cases for unset/false/true with no manually supplied demo props.
- Exact portal-login request count/body, empty-submit zero-call validation, and no alternate success
  callback.
- Failed logout transport still reaches `UNAUTHENTICATED_USER` and clears every authority field and
  protected route.
- Run the pinned Playwright scenarios successfully and capture the portal validation and post-
  logout states; collection-only output is not acceptance evidence.

## Evidence Required

Failing-first real-boundary output, green isolated flag matrix, successful Playwright log,
validation/post-logout screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Demo flag behavior and portal fail-closed session behavior are proven through the real app
  boundary in all three flag states.
- No test manually reconstructs the production flag-to-UI projection it claims to verify.

