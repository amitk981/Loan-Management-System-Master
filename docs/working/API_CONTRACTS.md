# API Contracts

Source contract baseline: `docs/source/api-contracts.md`.

This working file tracks implementation status and slice-level decisions. It must be updated whenever a slice changes frontend/backend assumptions.

| Contract Area | Status | Related Screens | Source Contract | Notes |
|---|---|---|---|---|
| Authentication and current user | Draft from source | Login, dashboards, portal auth | `docs/source/api-contracts.md`, `auth-permissions.md` | No backend implemented yet. |
| Members and KYC | Draft from source | Members, borrower profile, application intake | `data-model.md`, `api-contracts.md` | Prototype uses mock data. |
| Loan applications | Draft from source | Applications, completeness | `api-contracts.md` | Needs real draft/submit/check endpoints. |
| Appraisal and loan limit | Draft from source | Appraisal workbench | `functional-spec.md`, `api-contracts.md` | Financial rules require tests before implementation. |
| Sanction and approvals | Draft from source | Sanction workbench | `auth-permissions.md`, `api-contracts.md` | Approval matrix is high-control. |
| Documentation and securities | Draft from source | Documentation hub | SOP PDFs, `api-contracts.md` | Must preserve disbursement blockers. |
| SAP and disbursement | Draft from source | Disbursement and CFC | SOP PDFs, `api-contracts.md` | Integration is manual/adapter-first for MVP. |
| Loan account, repayment, interest | Draft from source | Loan account, repayments, interest | `data-model.md`, `api-contracts.md` | Financial calculations are high risk. |
| Default, recovery, closure | Draft from source | Default, closure | `functional-spec.md`, `api-contracts.md` | Recovery approvals require audit evidence. |
| Compliance, registers, reports | Draft from source | Compliance, registers, reports | `api-contracts.md`, `auth-permissions.md` | Export masking must be tested. |

## Contract Rules
- Do not implement API-consuming frontend code without a matching contract entry.
- Do not treat mock data shape as the final backend shape without checking `docs/source/api-contracts.md` and `docs/source/data-model.md`.
- Mark uncertain contracts as Draft and record assumptions in `ASSUMPTIONS.md`.
