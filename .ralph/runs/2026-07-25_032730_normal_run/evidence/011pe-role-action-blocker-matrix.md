# 011PE Role, Action, and Blocker Matrix

| Surface | Backend authority projected to UI | Allowed action | UI blocker / read-only proof |
|---|---|---|---|
| Grievance Register | `available_actions` on each scoped grievance | `resolve` only when the row contains that action | Rows without `resolve` show `Read only`; a page-level notice states that no resolution action is available for the current role/status. |
| Grievance resolution | Governed `POST /api/v1/grievances/{id}/resolve/` | Company Secretary or assigned authorised resolver selects the server-supported `resolved` target and enters a reason | Submission is blocked until both status and reason are present. Backend 400/403/409 messages remain visible; no optimistic state change occurs. |
| Audit Archive | `closure.archive.read` plus canonical archive scope | Search, view retained manifest, download manifest | Every user sees the read-only banner. No archive-create, edit, destruction, delete, or other mutation control exists. |
| Archive manifest download | Governed `GET /api/v1/loan-closures/{closure_id}/archive/` | Download a JSON representation only after that audited canonical detail read succeeds | A failed detail read produces no download and surfaces the backend error. Raw locations are never placed in a client-constructed request. |

State coverage:

| State | Grievance Register | Audit Archive |
|---|---|---|
| Loading | `Loading grievances…` | `Loading archive records…` |
| Empty | Tab/table empty message | Scoped collection empty message |
| Error | Register unavailable message | Archive unavailable message |
| Unauthorized | `Access Denied` for 401/403 | `Access Denied` for 401/403 |
| Validation | Status and reason errors; backend field error | Search remains backend validated |
| Blocked/read-only | Missing projected `resolve` suppresses action | Mutation controls absent for all roles |
| Success | Canonical refetch then success banner | Audited detail read then download success banner |

Focused proof: `GrievancesHub.test.tsx`, `AuditArchiveHub.test.tsx`, and
`recoveryApi.test.ts`; output is retained in `terminal-logs/011pe-frontend-green.log`.
