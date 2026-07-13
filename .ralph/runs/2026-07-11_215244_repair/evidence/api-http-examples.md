# Completeness Action HTTP Examples

These requests are exercised by
`LoanApplicationDraftApiTests.test_each_completeness_permission_projects_and_invokes_only_its_own_action`.
Each actor holds application read plus exactly the named mutation permission and is object-scoped
to the target application.

| Action | Method and path | Exact request body | Granted result | Any other action-only actor |
|---|---|---|---|---|
| Pass | `POST /api/v1/loan-applications/{id}/completeness-check/pass/` | `{}` | `200`, formal reference and register created | `403 PERMISSION_DENIED`, zero writes |
| Return | `POST /api/v1/loan-applications/{id}/return-with-deficiencies/` | `{"communication_mode":"email","message":"Please supply the missing PAN copy.","items":[{"item_code":"borrower_pan"}]}` | `200`, returned state and one open deficiency | `403 PERMISSION_DENIED`, zero writes |
| Resolve | `POST /api/v1/deficiencies/{id}/resolve/` | `{"resolution_notes":"Replacement PAN verified."}` | `200`, named open deficiency resolved | `403 PERMISSION_DENIED`, zero writes |
| Reject | `POST /api/v1/loan-applications/{id}/rejection-note/` | `{"rejection_stage":"completeness","rejection_reason_category":"eligibility","detailed_reason":"Borrower does not meet active member criteria.","reapply_allowed_flag":true,"communication_mode":"email"}` | `200`, one draft rejection note | `403 PERMISSION_DENIED`, zero writes |

The paired read is `GET /api/v1/loan-applications/{id}/completeness-check/`. Its four actions carry:

| Action code | Required permission | Required role |
|---|---|---|
| `pass_completeness` | `applications.loan_application.complete_check` | `deputy_manager_finance` |
| `return_with_deficiencies` | `applications.loan_application.return_deficiency` | `deputy_manager_finance` |
| `resolve_deficiency` | `applications.deficiency.resolve` | `deputy_manager_finance` |
| `create_rejection_note` | `applications.rejection_note.create` | `credit_manager` |

Every item also contains `label`, `enabled`, and nullable `disabled_reason`, completing the six-field
API §44 shape. Terminal evidence is in `terminal-logs/backend-authority-matrix-green.log`.
