# Execution Plan

Selected slice: `007O-frozen-terminal-decision-and-register-source-closure`

## Scope and seam

- Keep the existing HTTP interfaces and approval action payloads unchanged.
- Deepen the existing `approval_case_engine` seam so one locked, canonically validated frozen
  review package supplies terminal decision/register facts.
- Remove terminal value reads from mutable application/member/appraisal attributes while retaining
  their foreign-key ownership links and state transitions.
- Route General Meeting availability and mutation through `approval_case_is_readable`, preserving
  the existing legal-audience and permission decisions.

## TDD sequence

1. Add one public action-flow regression that mutates live application, member, appraisal,
   loan-limit, and risk values between routing and final approval; capture RED, then make the
   approved decision and register equal the routed frozen package.
2. Add the equivalent public rejection-flow regression and make the rejected register retain
   frozen application/borrower/amount/purpose-risk source facts.
3. Add a public final-action corruption regression that leaves live rows valid but corrupts the
   frozen package; prove a nondisclosing failure and zero writes across action, decision, register,
   workflow, audit, notification, and communication ledgers.
4. Extend the General Meeting behavioral/static matrix to prove availability and mutation use the
   single canonical readable-case decision with unchanged denial parity; capture RED/GREEN.
5. Refactor only after focused tests are green, keeping frozen-package validation and extraction
   local to the approval engine interface.

## Verification and delivery

- Run focused approval action/register/General Meeting tests after every red/green cycle using the
  mandated Ralph virtualenv interpreter.
- Run Django check, migration-sync check, full backend coverage gate, and all configured frontend
  build/typecheck/lint/test gates.
- Save self-contained terminal evidence, changed-files/risk/review/final artifacts, update the Epic
  007 digest if source extraction needs clarification, sharpen the next one or two eligible
  Not Started slices using already-opened source material, and update slice/state/progress/handoff.
- Do not create commits or modify protected/source files.
