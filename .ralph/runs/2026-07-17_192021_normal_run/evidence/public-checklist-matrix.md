# Public Post-Disbursement Checklist Matrix

| Case | Result | Write behavior |
|---|---|---|
| Active effective Senior Manager Finance, explicit grant, exact initiating-maker scope, current transfer/register/advice | 200 | One immutable action/audit/workflow/version chain; checklist links signature/account and becomes `ready` |
| Same actor, comment, and current evidence replay | 200 | Zero writes; same action identity |
| Changed comment after signature | 409 `CHECKLIST_ACTION_CONFLICT` | Zero writes |
| Before successful transfer | 409 `DISBURSEMENT_EVIDENCE_UNAVAILABLE` | Zero writes |
| Successful transfer but checklist before `sanction_approved`/complete prior signatures | 409 `CHECKLIST_APPROVAL_OUT_OF_ORDER` | Zero writes |
| Changed pending-advice/register/transfer evidence | 409 `DISBURSEMENT_EVIDENCE_UNAVAILABLE` | Zero writes |
| Missing register or pending-advice identity | 409 `DISBURSEMENT_EVIDENCE_UNAVAILABLE` | Zero route writes |
| Inactive signer/session | 401 | Zero writes |
| Permission only, no Senior Finance role | 403 | Zero writes |
| Senior Finance role only, no explicit grant | 403 | Zero writes |
| Different Senior Finance user outside Stage-5 initiating scope | 403 `OBJECT_ACCESS_DENIED` | Zero writes |
| Governed multi-role exact initiating maker | 200 | Canonical role frozen as `senior_manager_finance` |

Evidence: `terminal-logs/green-post-disbursement-checklist-matrix.txt` and
`terminal-logs/impacted-backend-green.txt`.
