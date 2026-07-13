# Active-Member Calculation Boundary Inventory

Production exposes `ActiveMemberStatusModule.calculate` as an actorless domain calculation, not as
an object-access API. Its real owning boundaries are:

- Staff eligibility: `EligibilityAssessmentModule.run` loads the persisted loan application,
  enforces the action-specific application boundary, and derives `application.member_id` before
  calculating. The caller cannot provide a separate member identifier.
- Authenticated member portal: portal HTTP authentication resolves a persisted `PortalAccount` and
  passes its related `member` into the portal service. Query/body `member_id` substitution is
  rejected by the portal ownership tests before calculation and creates no records.
- Borrower-limit projection: the authenticated portal application boundary resolves its owned
  member/application and passes the persisted member object to `project_borrower_limit`; the
  projection accepts no member identifier and recalculates only `member.member_id`.

Executable evidence is retained in the focused 83-test run (`focused-coverage.log`), including the
member authority matrix, active-member module, supply HTTP boundary, portal ownership API, credit
module boundaries, and borrower-limit projection. The obsolete exact-filename/source-string caller
whitelist was removed. The existing AST module-boundary guard remains for forbidden concrete model
imports, which are dependency facts not observable through a single public response.
