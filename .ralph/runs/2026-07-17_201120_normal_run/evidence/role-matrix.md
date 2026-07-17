# Disbursement Advice Role Matrix

| Actor condition | Result | Retained acting role |
|---|---|---|
| Active Senior Manager Finance + High grant + exact initiating maker + current SAP assignee | Allowed | `senior_manager_finance` |
| Active Credit Manager + High grant + exact active loan/application/member relation | Allowed | `credit_manager` |
| Credit Manager also carrying effective CFC approval authority | Allowed only through Credit Manager scope | `credit_manager` |
| CFC-only, including exact authorising checker + High grant | `403 OBJECT_ACCESS_DENIED` | None |
| Credit Manager against non-active loan scope | `403 OBJECT_ACCESS_DENIED` | None |
| Permission-only unrelated role | `403 OBJECT_ACCESS_DENIED` | None |
| Role-only without High grant | `403 FORBIDDEN` | None |
| Inactive user or inactive primary role | Authentication/permission denial | None |

Verified by `test_public_role_matrix_allows_scoped_credit_manager_and_denies_cfc_only`,
`test_permission_scope_and_stale_transfer_fail_closed`, and
`test_disbursement_advice_grant_matches_stage_five_role_matrix`.

