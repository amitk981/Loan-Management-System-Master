# API Contracts

Source contract baseline: `docs/source/api-contracts.md`.

This working file tracks implementation status and slice-level decisions. It must be updated whenever a slice changes frontend/backend assumptions.

| Contract Area | Status | Related Screens | Source Contract | Notes |
|---|---|---|---|---|
| Backend health endpoints | Implemented in slice 002A | None | `technical-architecture.md` R1 health checks; standard response envelope from `api-contracts.md` | `GET /api/v1/health/live/`, `/ready/`, and `/deep/` return `{ success, data, meta }`; ready/deep include database connectivity status. |
| Authentication and current user | Partially implemented in slice 002B | Login, dashboards, portal auth | `docs/source/api-contracts.md`, `auth-permissions.md` | Implemented `POST /api/v1/auth/login/`, `/refresh/`, and `/logout/` with standard envelopes, active-user-only login, refresh rotation, session revocation, role/team token claims, and auth audit logs. `/api/v1/auth/me/`, password reset, change password, admin session controls, and full permission catalogue remain future slices. |
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

## Implemented Auth Subset

Implemented endpoints:

| Endpoint | Request | Success Data | Key Rules |
|---|---|---|---|
| `POST /api/v1/auth/login/` | `email`, `password` | bearer `access_token`, `refresh_token`, `expires_in`, user profile with role/team codes | Only `active` users receive tokens; invalid credentials and non-active users receive `401 INVALID_CREDENTIALS`; successful and failed attempts are audited. |
| `POST /api/v1/auth/refresh/` | `refresh_token` | rotated bearer token payload | Refresh tokens are matched against `user_sessions.refresh_token_hash`; successful refresh rotates the token; replayed, revoked, expired, malformed, or status-invalid tokens return `401`. |
| `POST /api/v1/auth/logout/` | `refresh_token` | `{ "logged_out": true }` | Logout revokes the matching session with reason `logout`; the same refresh token cannot be used again; logout is audited. |

Full example responses for this slice are saved in `.ralph/runs/2026-07-02_154724_normal_run/api-response-examples.md`.
