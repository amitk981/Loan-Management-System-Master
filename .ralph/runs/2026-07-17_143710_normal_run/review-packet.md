# Review Packet: 2026-07-17_143710_normal_run

## Result
Complete pending independent orchestrator validation and commit.

## Slice
009H-disbursement-advice-and-communication

## Outcome

- Added exact `POST /api/v1/disbursements/{id}/send-advice/` request/envelope behavior.
- Added one deep advice module behind `DisbursementWorkflow.send_advice`, plus replaceable Manual and
  Fake email adapters with no network I/O.
- Reconciles exact 009G transfer/account/history/audit/workflow truth, canonical borrower email, and
  exactly one approved effective template before delivery.
- Retains one sent communication/link and singular safe audit/workflow action only after acceptance.
  Exact replay is zero-write/no-resend; changed/stale/provider-failed attempts create no false truth.
- Added both source role grants, public behavior tests, and two PostgreSQL five-caller methods.
- Updated API contract/digest/assumption/state/progress/handoff and sharpened unsharpened 009J.

## Traceability

- Source says disbursement advice is shared with the farmer after disbursement
  (`integrations.md` §9.1; BR-054/M08-FR-010); code requires coherent 009G success and canonical
  member email; verified by `test_public_success_sends_exact_advice_without_financial_side_effects`
  and `test_pending_transfer_cannot_send_advice`.
- Source §31.5 says the request contains `channel` and `recipient_email`; code rejects unknown fields/
  query parameters, accepts email only, and refuses a noncanonical address; verified by
  `test_validation_template_and_delivery_failures_create_no_advice_truth`.
- Integrations §§10/19.3/21 require template-backed, evidenced, duplicate-safe borrower delivery;
  code validates the exact template/adapter contract and singular retained evidence; verified by
  replay, ledger-drift, provider-rejection, and PostgreSQL race tests.
- Slice says advice must not change financial/register/checklist truth; the success test compares
  the complete account row, checklist rows, repayments, and register flag before/after.

## Verification

- RED logs: `red-advice-success.log`, `red-advice-replay.log`, `red-advice-ledger.log`.
- GREEN/focused: 8 collected tests, 6 pass and 2 PostgreSQL-only races skip under SQLite.
- Impacted: 81 tests pass; 10 existing/declared PostgreSQL-only tests skip under SQLite.
- `manage.py check`: pass. `makemigrations --check --dry-run`: no changes. Ruff: pass.
- Local PostgreSQL attempt: blocked by sandbox socket `Operation not permitted`; the slice declares
  `postgresql-five-race-acceptance` for independent twice-run validation.
- No frontend or screenshots were required by this backend-only slice.

## Recommended Next Action
Run the independent full coverage and twice-run PostgreSQL capability gates. If green, commit 009H;
the state correctly schedules the four-slice architecture review before 009I.
