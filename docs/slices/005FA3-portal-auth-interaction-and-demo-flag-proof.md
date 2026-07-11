# Slice 005FA3: Portal Auth Interaction and Demo-Flag Proof

## Status
Not Started

## Parent Epic
Epic 005: Application Intake and Completeness
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal

Close the evidence and behavior-test gap left by the owner-applied 005FA2 fix by proving the real
portal login form, pre-login shell, logout, and demo flag through rendered interactions rather than
raw-source assertions.

## Depends On
- 005FA2

## Source / Review References
- `docs/source/auth-permissions.md` portal authentication requirements
- `docs/source/security-privacy.md` session and authentication controls
- `docs/source/codebase-design.md` §23.3 and §26.3
- `docs/slices/005FA2-portal-demo-login-gating-and-session-authority.md`
- `docs/working/REVIEW_FINDINGS.md` entry for architecture review `2026-07-11_135129_architecture_review`

## Scope

- Mount the real `MP00_Login` form and submit empty credentials; assert the existing validation
  message renders and the real-session callback is not called.
- Submit populated credentials and assert exactly one call to `onSubmitLogin` with the entered
  identifier/password; prove there is no alternate success callback or demo borrower transition.
- Render the real pre-login app/context boundary with `VITE_ENABLE_DEMO_AUTH` false/unset and prove
  no protected staff/member content, role switcher, or demo login affordance is reachable before a
  backend session is installed.
- Exercise logout from a backend session and prove identity, role codes, permissions, actions, and
  protected content are cleared even when the network logout call fails.
- In a separately reset module environment with `VITE_ENABLE_DEMO_AUTH=true`, prove only the
  already-approved development demo surfaces appear; do not add a portal credential bypass.
- Keep the 005FA2 production behavior and existing visual composition unchanged unless a failing
  interaction test exposes a real defect.

## Test Cases

- Testing Library empty and populated portal-form submissions with real DOM events and call counts.
- Default/false and true demo-flag module-isolation tests over the real login/header/app boundary.
- Pre-login and post-logout permission/route-denial tests using the real `RoleProvider` state.
- Regression that a failed logout request still leaves `UNAUTHENTICATED_USER` and no protected UI.

## Evidence Required

Failing-first interaction output, green focused output, corrected-login validation screenshot, and
all configured gates.

## Risk Level
High

## Acceptance Criteria

- Portal entry has one real-session success path and no demo fallback when the flag is off.
- Pre-login and post-logout state cannot expose any permission-gated UI.

## Run-Ahead Sharpening Review (005E2, 2026-07-11)

- Confirmed against the Epic 005 digest already opened for 005E2: the interaction suite must mount
  the real portal login and `RoleProvider` boundary, not a copied form or synthetic permission
  projection. Empty submission makes zero session calls; populated submission makes exactly one;
  logout clears identity/role/permission/action fields even when its transport rejects.
- The `VITE_ENABLE_DEMO_AUTH` true and false/unset cases must reset the module environment between
  runs so build-time flag state cannot leak. No production styling or portal credential behavior is
  in scope unless these public-boundary tests expose a defect.
