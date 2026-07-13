# Approval Configuration API Examples

## Create rule

`POST /api/v1/approval-matrix-rules/` with `approvals.matrix.manage` returns a standard success
envelope whose data includes the new rule UUID, `loan_sanction`, inclusive decimal bounds,
`["cfo", "director"]`, director count, register, effective dates, active status, and version.

```json
{
  "decision_type": "loan_sanction",
  "amount_min": "0.00",
  "amount_max": "500000.00",
  "condition_code": null,
  "required_approver_roles": ["cfo", "director"],
  "required_director_count": 1,
  "joint_approval_required_flag": true,
  "register_required": "credit_sanction_register",
  "effective_from": "2026-04-01",
  "effective_to": null,
  "version_number": "1"
}
```

The response `data` repeats those facts, adds `approval_matrix_rule_id` and `status: "active"`,
and is wrapped by `success`, `data`, and `meta`.

## List rules

`GET /api/v1/approval-matrix-rules/` with `approvals.matrix.read` returns the same immutable response
items. A missing token returns `401`; a user without read permission returns `403 FORBIDDEN`.

## Supersede rule

`PATCH /api/v1/approval-matrix-rules/{id}/` creates a replacement UUID/version and closes the old
row on the day before the replacement begins. Overlapping configuration returns
`409 CONFIGURATION_CONFLICT`; invalid/non-finite money returns `400 VALIDATION_ERROR`. Tests compare
the complete rule, committee, version-history, and business-audit state before and after denial.

## Sanction committees

`GET/POST /api/v1/sanction-committees/` and `PATCH /api/v1/sanction-committees/{id}/` use the same
permission and immutable-supersession contract. Responses identify the CFO, two Directors, Board
meeting reference, effective range, status, and version.

```json
{
  "committee_name": "FY 2026 Committee",
  "cfo_user_id": "<uuid>",
  "director_1_user_id": "<uuid>",
  "director_2_user_id": "<uuid>",
  "board_meeting_reference": "BOARD-2026-01",
  "effective_from": "2026-04-01",
  "effective_to": null,
  "version_number": "1"
}
```
