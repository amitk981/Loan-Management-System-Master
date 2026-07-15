# Impact Analysis

## Change request

CR-006 fixes host-dependent approval decision timestamps in the approval registers. Stored/API
instants remain UTC; the browser must render them in the SFPCL business timezone,
`Asia/Kolkata`.

## Backend impact and grep evidence

No backend model, endpoint, serializer, or service change is required.

- `sfpcl_credit/approvals/models.py` stores approval actions in the timezone-aware
  `ApprovalAction.acted_at` `DateTimeField`.
- `sfpcl_credit/approvals/modules/approval_case_engine.py::_action_time` serializes the instant as
  ISO 8601 and normalizes UTC to `Z`.
- `sfpcl_credit/approvals/modules/sanction_register.py` returns frozen
  `approver_decisions_json` through the Credit Sanction Register endpoint without display
  formatting.
- Grep found the HTTP boundaries at `/api/v1/credit-sanction-register/` and
  `/api/v1/exception-register/`; existing backend tests in
  `test_approval_case_routing_api.py` and `test_sanction_submission_api.py` assert that
  `acted_at` values are present and preserved.

Because the contract and stored instants are unchanged, no backend regression test is added for
this frontend-only defect.

## Frontend impact

- `sfpcl-lms/src/pages/registers/ApprovalRegisterPanels.tsx` owns the shared `dateTime`
  formatter. It is used by Credit Sanction Register `approver_decisions` and Exception Register
  `approval_actions` (and by sanction communication timestamps when present).
- `sfpcl-lms/src/pages/registers/RegistersHub.tsx` routes users to both owned register panels; its
  layout, routes, role checks, loading states, and API calls are unaffected.
- `sfpcl-lms/src/services/approvalRegistersApi.ts` supplies the UTC timestamp strings but performs
  no formatting; its API contract is unaffected.

## Blast radius and regression coverage

The formatter is local to `ApprovalRegisterPanels.tsx`. Its other consumers are therefore limited
to the two approval-register modules in that file:

1. Credit Sanction Register decision evidence.
2. Exception Register approver-comment evidence.
3. Credit Sanction Register communication evidence when `sent_at` is populated.

Existing coverage is in `sfpcl-lms/src/pages/registers/RegistersHub.test.tsx`. The regression will
assert the same UTC stored instant is rendered as an Asia/Kolkata business time through both the
S23 Credit Sanction Register and S25 Exception Register public UI. The focused test file will be
run with both `TZ=UTC` and `TZ=Asia/Kolkata` to prove host-timezone independence. No other module
imports the local formatter, so no additional per-module test file is needed.

## Frontend design compliance

This changes only date-time formatting. It introduces no styling, colours, typography, spacing,
layout, components, mock data, client-side business decisions, or route changes, and therefore
complies with `docs/working/FRONTEND_DESIGN_RULES.md`.
