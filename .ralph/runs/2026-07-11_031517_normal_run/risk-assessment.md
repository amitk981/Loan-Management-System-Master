# Risk Assessment

Risk level: Medium (standing autonomous approval; no veto applies).

- Security/contract surface: changes the public code for authenticated missing-global-permission
  denials across staff and portal APIs, but does not change the HTTP 403 status or any authorization
  decision.
- Blast radius: shared envelope plus 13 production module/view families. The only retained legacy
  literal is the documented compatibility normalization inside `sfpcl_credit/api.py`; a static AST
  regression rejects it everywhere else in production.
- Preserved boundaries: token/auth codes, object scope, sensitive reveals, approval authority,
  permission grants, role assignments, messages, success responses, audit rows, and workflow events.
- Data/migration risk: none; no model or migration changes.
- Frontend risk: no production frontend code branched on the retired code; the complete frontend
  gates confirm generic error behavior remains intact.
- Controls: failing-first contract tests, specialized-code translation regression, representative
  168-test endpoint sweep, full 389-test backend suite at 94% coverage, and all frontend gates.
- Residual risk: an untested external consumer may branch on `PERMISSION_DENIED`; source contract
  fidelity requires `FORBIDDEN`, and the compatibility adapter accepts legacy internal typed input
  while preventing legacy public output.
