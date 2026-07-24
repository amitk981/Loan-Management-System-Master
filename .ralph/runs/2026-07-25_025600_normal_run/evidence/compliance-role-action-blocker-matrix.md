# Compliance Role, Action, Blocker, and Mock-Removal Matrix

| Surface | Canonical source | Staff action projection | Auditor result | Blocker/state proof |
|---|---|---|---|---|
| S62 controls/tasks | `compliance-controls`, `compliance-tasks` | Evidence review only when `review_evidence` is projected | Backend auditor projection has no mutation action | Empty, unauthorized, service error, and evidence-review validation tests |
| S63 Section 186 | `compliance/section-186-trackers` | Review only when `review` is projected | Backend auditor projection has no review action | Accepted over-limit reviews surface the backend Board-presentation blocker |
| S64 NBFC test | `compliance/nbfc-principal-tests` | Review only when `review` is projected | Backend auditor projection has no review action | Triggered accepted reviews use the same backend Board-evidence blocker |
| S65 KYC/re-KYC | `kyc-reviews` | Read-only in this slice; backend status/due window is rendered | Read-only | Due, 30-day warning, overdue, and empty projections are rendered without local date policy |
| S66 stamp duty | `reports/stamp-duty` over 008D-owned records | Read-only register | Read-only | Empty/unauthorized errors are transport-owned |
| S67 money-lending | `reports/money-lending-review` | Read-only annual review | Read-only | Empty/unauthorized errors are transport-owned |
| Final mock owner | `ComplianceDashboard.tsx` | No `mockData` import or inline tracker business fixture | Same real API seam | Raw-source regression rejects former fixture names and amounts |

## Canonical refetch

Every successful evidence, Section 186, or NBFC review awaits the backend action and then reloads all
seven dashboard projections. `ComplianceDashboard.test.tsx` proves the second read and updated
canonical success state; `recoveryApi.test.ts` proves exact request methods, paths, and bodies.

## Trusted browser status

The exact declared spec was attempted with both local servers healthy. Chrome aborted before the
first test body, and the immediate repository browser probe reproduced the same launch failure.
No screenshot was created or substituted. Independent trusted validation must run the declared
spec twice and produce `compliance-trackers.png`.
