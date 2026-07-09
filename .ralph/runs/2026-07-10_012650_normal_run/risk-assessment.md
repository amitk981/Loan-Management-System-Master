# Risk Assessment

## Slice
005G2-member-portal-session-and-audit-contract-hardening

## Risk Level
High.

## Why
- This slice changes session validation for borrower portal users and affects access-token and
  refresh-token behavior.
- It changes audit action names for portal flows, which are compliance-visible contract data.
- It touches a shared loan application service, though only by adding defaulted audit-action
  override parameters.

## Mitigations
- TDD red/green coverage was added for stale portal sessions, source-backed portal audit names, and
  portal application audit names.
- Full backend tests passed, including staff loan-application tests proving staff
  `applications.loan_application.*` audit names still work.
- The implementation does not add migrations or dependencies.
- Portal denial side-effect tests cover no application/audit/workflow creation after suspension.
- API contracts, assumptions, digest, and next slices were updated with the route-level `401`
  invalid-session behavior.

## Residual Risk
- Existing JWT access tokens still physically contain their issued claims until expiry, but every
  implemented protected backend route uses the session-bound validator before exposing data or
  actions. Future routes must keep using `http_auth`/`auth_service.validate_access_session`.
