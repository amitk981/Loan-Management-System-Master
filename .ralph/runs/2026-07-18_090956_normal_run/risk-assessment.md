# Risk Assessment

Risk level: High.

- Selected slice: 009H3BB-communications-finalization-and-race-closure
- Mode: normal_run

This slice changes the terminal external-communication/idempotency path. Material failure modes are
duplicate borrower advice, accepted provider truth lost across a crash, partial receipt or local
success evidence, stale financial/template/contact facts blessing historical acceptance, sensitive
advice leaking into general evidence, and concurrent callers recording multiple actions.

Controls completed:

- The provider result is committed in the pre-existing frozen outbox before local finalization.
  Failing-first tests independently force failure before receipt retention and before protected
  Communication commit; both leave no partial local chain and exact fresh retry completes once.
- Communications alone owns receipt, protected Communication, safe audit/workflow, delivery digest,
  finalization, and replay reconciliation. Static dependency tests and source scans prove it imports
  no disbursement code and the legacy module retains no duplicate policy.
- Disbursements re-locks and reconciles current authority, contact, transfer, register, intent,
  account, and upstream evidence before consuming the immutable decision in the same transaction.
- Audit/workflow tests reject raw email, rendered subject/body, full UTR, provider message id,
  disbursement amount, and injected extra evidence; only masks/digests remain in general ledgers.
- The full 30-test role/scope/current-truth/replay/rejection/malformed/no-financial-write matrix is
  green. Both PostgreSQL race methods passed in two separate final runs with one winner, four clean
  losers, and one complete retained chain per method.
- No schema/migration, public API shape, frontend, money, transfer, loan-account, register,
  checklist, repayment, schedule, interest, default, closure, or portal behavior changed.

Residual risk: a future real provider must honor the supplied idempotency key across process and
network failures. Manual/Fake/Future adapter contracts preserve and expose that obligation, but no
paid or external sandbox call was made. Independent complete coverage remains authoritative.
Standing High-risk approval applies; no owner veto is recorded.
