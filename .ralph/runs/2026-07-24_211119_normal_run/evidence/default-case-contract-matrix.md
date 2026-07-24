# 011PA Default Case Contract Matrix

## Role, action, and blocker coverage

| Surface | Authority / source | Rendered behavior | Evidence |
|---|---|---|---|
| S53 list | `GET /api/v1/default-cases/?page_size=100` | Uses backend rows and pagination total; no inline cases | `src/services/recoveryApi.test.ts`, `src/pages/defaults/DefaultRecoveryHub.test.tsx` |
| S53 detail | `GET /api/v1/default-cases/{id}/` | Selected case is refetched; stale responses cannot replace a newer selection | `keeps the latest selected case authoritative...` |
| S54 grace | `grace_period_start_date`, `grace_period_end_date`, `grace_state` | Dates/state display exactly from the projection | `renders list/detail, grace, extension...` |
| S54 assessment/extension | `current_assessment`, `extension_note` | Recorded evidence displays read-only; absent objects render blocked cards | populated and absent-state render tests |
| S55 frozen note | `non_payment_note.frozen_case_facts` | Frozen money, reason, outcomes, preparer, document, and status display without inputs or mutations | request test plus frozen-note render test |
| List/detail unauthorized | Standard 401/403 `AuthSessionError` | Distinct `Access Denied` state at both collection and selected-detail boundaries | unauthorized render tests |
| S56 recovery decision | 011PB-owned server action contract | Tab is disabled even when the 011A-011F projection contains an approved decision/action | focused render test and trusted-browser spec |
| S57 execution | 011PB-owned server action contract | Tab is disabled; page issues no recovery mutation | focused render test and reverse-consumer browser spec |

## Mock-removal ratchet

| File | S53-S55 business fixtures | Presentation metadata |
|---|---|---|
| `src/pages/defaults/DefaultRecoveryHub.tsx` | No `mockData` import, `defaultCases` array, inline member/loan/money fixture, or mutable note form remains | Tab labels and server-state display labels remain |
| `src/services/recoveryApi.ts` | No fixture or calculation; list/detail delegate to authenticated transport | Type declarations only |

The retained recovery mutation helpers in `recoveryApi.ts` belong to the already-delivered backend
consumer seam and future 011PB wiring. They are not imported or reachable from the 011PA page.
