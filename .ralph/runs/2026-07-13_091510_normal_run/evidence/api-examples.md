# 007B API Evidence

## Successful enrichment

`POST /api/v1/loan-applications/{id}/approval-cases/`

```json
{
  "approval_type": "sanction",
  "amount": "500000.00",
  "reason_for_approval": "Loan appraisal recommended approval.",
  "force_exception_route": false
}
```

The success envelope retains the 006G `approval_case_id` and `workflow_event_id`, and returns
`approval_matrix_rule_id/version`, `sanction_committee_id/version`, `decision_date`, amount,
concrete ordered `required_approvers`, empty `excluded_approvers`, related application facts,
complete matrix/committee projections, loan-limit provenance, and `version: 2`.

## Stable losers

- No bearer token: `401 AUTH_REQUIRED`.
- Missing `approvals.case.create`: `403 FORBIDDEN`.
- Missing/stale policy provenance: `409 INVALID_STATE_TRANSITION`.
- No effective approved rule: `400 NO_EFFECTIVE_APPROVAL_RULE`.
- Conflicting immutable repeat or decided case: `409 INVALID_STATE_TRANSITION`.

Exact request/response assertions and complete no-write ledger comparisons are retained in
`evidence/terminal-logs/007b-*.txt` and the focused/full test logs.
